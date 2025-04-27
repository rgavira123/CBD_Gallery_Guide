from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from gestion_rutas.graph_models import Route
from gestion_rutas.forms import CreateRouteForm
from gestion_museos.graph_models import Museum, Room, Artwork, Artist, Movement
from neomodel import db, MultipleNodesReturned

def get_neo4j_object_or_404(cls, **kwargs):
    try:
        return cls.nodes.get(**kwargs)
    except cls.DoesNotExist:
        raise Http404(f"No {cls.__name__} found with {kwargs}")

def get_neo4j_property(node, prop_name, default=None):
    """Extrae una propiedad de un nodo Neo4j de forma segura."""
    if hasattr(node, '_properties') and isinstance(node._properties, dict):
        return node._properties.get(prop_name, default)
    
    if hasattr(node, 'properties') and hasattr(node.properties, 'get'):
        return node.properties.get(prop_name, default)
    
    if hasattr(node, prop_name):
        return getattr(node, prop_name)
    
    # Si todo falla, intentar acceder a __dict__
    if hasattr(node, '__dict__'):
        node_dict = node.__dict__
        if '_properties' in node_dict and isinstance(node_dict['_properties'], dict):
            return node_dict['_properties'].get(prop_name, default)
    
    return default

def debug_neo4j_node(node, label="Nodo"):
    """Función para depurar un nodo de Neo4j e imprimir su estructura interna."""
    print(f"\n----- Depuración de {label} -----")
    print(f"Tipo: {type(node)}")
    print(f"Dir: {dir(node)}")
    
    # Intentar acceder a diferentes propiedades comunes
    for attr in ['properties', '_properties', 'id', '_id', 'element_id', '_element_id', 'labels', '_labels']:
        if hasattr(node, attr):
            print(f"{attr}: {getattr(node, attr)}")
    
    # Ver el objeto __dict__ completo
    if hasattr(node, '__dict__'):
        print(f"__dict__: {node.__dict__}")
    
    print("----- Fin de depuración -----\n")

def verify_museum_structure(museum_slug):
    """Verifica la estructura del museo para la generación de rutas"""
    
    # Verificar tipos de datos para depuración
    type_query = """
    MATCH (m:Museum {slug: $museum_slug})-[:HAS_ROOM]->(r:Room)
    RETURN 
      r.name as room_name,
      r.is_entrance as is_entrance,
      r.is_exit as is_exit,
      type(r.is_entrance) as entrance_type,
      type(r.is_exit) as exit_type
    LIMIT 5
    """
    
    try:
        type_results, _ = db.cypher_query(type_query, {'museum_slug': museum_slug})
        print("Tipos de datos en propiedades de salas:")
        for result in type_results:
            print(f"Sala: {result[0]}, is_entrance: {result[1]} ({result[3]}), is_exit: {result[2]} ({result[4]})")
    except Exception as e:
        print(f"Error al verificar tipos: {e}")
    
    # Consulta principal de verificación
    verify_query = """
    MATCH (m:Museum {slug: $museum_slug})-[:HAS_ROOM]->(r:Room)
    WITH m, collect(r) as rooms
    RETURN 
      size(rooms) as total_rooms,
      size([r IN rooms WHERE r.is_entrance = true OR r.is_entrance = 'true']) as entrance_rooms,
      size([r IN rooms WHERE r.is_exit = true OR r.is_exit = 'true']) as exit_rooms
    """
    
    try:
        verify_results, _ = db.cypher_query(verify_query, {'museum_slug': museum_slug})
        if verify_results and len(verify_results[0]) == 3:
            total_rooms, entrance_rooms, exit_rooms = verify_results[0]
            print(f"Verificación del museo: {total_rooms} salas total, {entrance_rooms} entradas, {exit_rooms} salidas")
            return total_rooms, entrance_rooms, exit_rooms
        else:
            print("La consulta de verificación no devolvió el formato esperado")
            return 0, 0, 0
    except Exception as e:
        print(f"Error en la verificación: {e}")
        return 0, 0, 0

def create_route_view(request, museum_slug):
    museum = Museum.nodes.get(slug=museum_slug)

    artworks = []
    for room in museum.rooms.all():
        for artwork in room.artworks.all():
            if artwork not in artworks:
                artworks.append(artwork)

    artwork_data = []
    for art in artworks:
        artist_names = [artist.name for artist in art.artist.all()]
        artwork_data.append({
            'id': art.element_id,
            'title': art.title,
            'artists': artist_names,
            'masterpiece': art.masterpiece,
            'rating': art.rating
        })

    authors = set()
    movements = set()
    for art in artworks:
        for artist in art.artist.all():
            authors.add((artist.element_id, artist.name))
        for movement in art.movement.all():
            movements.add((movement.element_id, movement.name))

    authors = sorted(list(authors), key=lambda x: x[1])
    movements = sorted(list(movements), key=lambda x: x[1])

    if request.method == "POST":
        form = CreateRouteForm(request.POST)
        form.fields['preferred_authors'].choices = authors
        form.fields['preferred_movements'].choices = movements

        if form.is_valid():
            request.session['route_form_data'] = form.cleaned_data
            request.session['museum_slug'] = museum_slug
            return redirect('gestion_rutas:generate_route')
    else:
        form = CreateRouteForm()
        form.fields['preferred_authors'].choices = authors
        form.fields['preferred_movements'].choices = movements

    return render(request, "create_route.html", {
        "form": form,
        "museum": museum
    })

def generate_route_view(request):
    if 'route_form_data' not in request.session or 'museum_slug' not in request.session:
        messages.error(request, "Debes completar primero el formulario de creación de ruta.")
        return redirect('gestion_museos:listado_museos')

    form_data = request.session.pop('route_form_data')
    museum_slug = request.session.pop('museum_slug')

    museum = get_neo4j_object_or_404(Museum, slug=museum_slug)

    name = form_data['name']
    description = form_data.get('description', '')
    # Asegúrate de que time_available sea un número
    time_available = int(form_data['time_available'])
    print(f"Tipo de time_available: {type(time_available)}, valor: {time_available}")
    preferred_authors_ids = form_data.get('preferred_authors', [])
    preferred_movements_ids = form_data.get('preferred_movements', [])
    is_public = form_data.get('is_public', False)

    # Depuración de parámetros
    print(f"Generando ruta para museo: {museum_slug}")
    print(f"Tiempo disponible: {time_available}")
    print(f"Autores preferidos: {preferred_authors_ids}")
    print(f"Movimientos preferidos: {preferred_movements_ids}")

    # Al comienzo de generate_route_view
    print(f"Tipo de preferred_authors_ids: {type(preferred_authors_ids)}")
    print(f"Valor de preferred_authors_ids: {preferred_authors_ids}")
    print(f"Tipo de preferred_movements_ids: {type(preferred_movements_ids)}")
    print(f"Valor de preferred_movements_ids: {preferred_movements_ids}")

    # Dentro de generate_route_view
    total_rooms, entrance_rooms, exit_rooms = verify_museum_structure(museum_slug)

    if entrance_rooms == 0:
        messages.error(request, "El museo no tiene salas marcadas como entrada.")
        return redirect('/museos/')

    if exit_rooms == 0:
        messages.error(request, "El museo no tiene salas marcadas como salida.")
        return redirect('/museos/')

    # Verificar tiempo mínimo
    min_time_required = total_rooms * 5  # Estimar 5 minutos por sala como mínimo
    if time_available < min_time_required:
        messages.error(request, 
            f"El tiempo disponible ({time_available} min) es demasiado corto. " 
            f"Se necesitan al menos {min_time_required} minutos para recorrer este museo.")
        try:
            # Intentar usar el namespace primero
            return redirect('gestion_museos:listado_museos')
        except:
            # Si falla, usar URL absoluta
            return redirect('/museos/')
    
    # Seguir con la consulta principal...
    
    # Modificar la consulta para que funcione sin preferencias si es necesario
    query = """
    MATCH (m:Museum {slug: $museum_slug})-[:HAS_ROOM]->(start:Room {is_entrance: true})
    CALL apoc.path.expandConfig(start, {
        relationshipFilter: 'CONNECTED_TO>',
        labelFilter: 'Room',
        uniqueness: 'NODE_PATH',
        maxLevel: 30,
        limit: 500,
        bfs: true
    })
    YIELD path

    WITH path, nodes(path) AS rooms, relationships(path) AS transitions
    WHERE last(rooms).is_exit = true  // Asegurar que termina en una salida
    
    WITH path, rooms, transitions,
         reduce(transit = 0, r IN transitions | transit + coalesce(r.transit_time, 0)) AS total_transit_time,
         [room IN rooms |
            {
                room: room,
                artworks: [(room)-[:EXHIBITS]->(a:Artwork)
                    WHERE (size($preferred_authors) = 0 OR any(aut IN [(a)-[:CREATED_BY]->(ar) | elementId(ar)] WHERE aut IN $preferred_authors))
                    OR (size($preferred_movements) = 0 OR any(mov IN [(a)-[:BELONGS_TO]->(mo) | elementId(mo)] WHERE mov IN $preferred_movements))
                | a]
            }
         ] AS room_info
         
    WITH path, rooms, room_info, total_transit_time,
         reduce(stay = 0, ri IN room_info | stay + CASE WHEN size(ri.artworks) > 0 THEN 5 ELSE 0 END) AS total_stay_time
         
    WITH path, rooms, room_info, total_transit_time, total_stay_time,
         (total_transit_time + total_stay_time) AS total_time
    WHERE last(rooms).is_exit = true AND total_time <= toInteger($time_available)
    
    RETURN path, rooms, room_info, total_time
    ORDER BY total_time DESC
    LIMIT 1
    """

    params = {
        'museum_slug': museum_slug,
        'preferred_authors': preferred_authors_ids,
        'preferred_movements': preferred_movements_ids,
        'time_available': time_available,
    }

    # Después de ejecutar la consulta
    results, meta = db.cypher_query(query, params)

    # Depuración de resultados - Añadir información más detallada
    print(f"Resultados obtenidos: {len(results)}")

    if not results or len(results) == 0:
        print("⚠️ No se encontraron rutas posibles dentro del tiempo disponible")
        messages.error(request, 
            f"No se pudo generar una ruta dentro del tiempo disponible ({time_available} min). "
            f"Prueba con un tiempo mayor o diferentes preferencias.")
        return redirect('/museos/')  # URL absoluta para mayor seguridad

    # Si llegamos aquí, tenemos resultados
    print(f"Tiempo total calculado: {results[0][3]}")
    print(f"Número de salas: {len(results[0][1])}")

    # En la parte superior de generate_route_view
    if results:
        # Depurar el primer nodo de sala para entender su estructura
        first_room = results[0][1][0] if results[0][1] else None
        if first_room:
            debug_neo4j_node(first_room, "Primera sala")

    record = results[0]
    rooms_nodes = record[1]
    room_info = record[2]
    total_time = record[3]

    route = Route(
        name=name,
        description=description,
        total_time=total_time,
        total_value=0,
        is_public=is_public,
        creator_username=request.user.username
    )
    route.save()
    
    # Depurar la conexión al museo
    print(f"Conectando ruta con museo {museum.name}")
    try:
        route.museum.connect(museum)
        print("✅ Relación con museo creada correctamente")
    except Exception as e:
        print(f"❌ Error al conectar con museo: {str(e)}")
    
    # Procesar las salas y las obras con mejor depuración
    total_value = 0
    rooms_connected = 0
    stops_connected = 0
    artworks_connected = 0
    
    # Depurar primero la estructura de room_info
    print(f"Estructura de room_info: {type(room_info)}")
    
    for i, info in enumerate(room_info):
        print(f"Procesando info {i+1}/{len(room_info)}")
        
        # Verificar qué contiene cada info
        print(f"Contenido de info: {type(info)}")
        
        room_node = info.get('room') if isinstance(info, dict) else None
        if not room_node:
            print(f"⚠️ No se encontró el nodo de sala en info {i+1}")
            continue
            
        # Usar nuestra función auxiliar
        slug = get_neo4j_property(room_node, 'slug')
        name = get_neo4j_property(room_node, 'name', 'Sala sin nombre')
        print(f"Procesando sala: {name} (slug: {slug})")
        
        if slug:
            try:
                # Buscar la sala en Django/Neo4j usando neomodel
                room = Room.nodes.get_or_none(slug=slug)
                if room:
                    print(f"✅ Sala encontrada en la BD: {room.name} (slug: {room.slug})")
                    
                    # Conectar la sala a la ruta sin guardar explícitamente
                    try:
                        route.rooms.connect(room)
                        print(f"✅ Sala {room.name} conectada correctamente")
                        rooms_connected += 1
                    except Exception as e:
                        print(f"❌ Error al conectar sala {room.name}: {str(e)}")
                    
                    # Procesar las obras
                    artworks = info.get('artworks', []) if isinstance(info, dict) else []
                    print(f"Obras de arte encontradas: {len(artworks)}")
                    
                    if artworks:
                        # Es una parada, conectar como STOPS_AT
                        try:
                            route.stops.connect(room)
                            print(f"✅ Parada {room.name} conectada correctamente")
                            stops_connected += 1
                        except Exception as e:
                            print(f"❌ Error al conectar parada {room.name}: {str(e)}")
                        
                        for artwork_node in artworks:
                            # Extraer propiedades de la obra
                            artwork_slug = get_neo4j_property(artwork_node, 'slug')
                            artwork_title = get_neo4j_property(artwork_node, 'title', 'Obra sin título')
                            print(f"Procesando obra: {artwork_title} (slug: {artwork_slug})")
                            
                            if artwork_slug:
                                try:
                                    artwork = Artwork.nodes.get_or_none(slug=artwork_slug)
                                    if artwork:
                                        print(f"✅ Obra encontrada: {artwork.title}")
                                        try:
                                            route.sees.connect(artwork)
                                            print(f"✅ Obra {artwork.title} conectada correctamente")
                                            artworks_connected += 1
                                            total_value += artwork.rating if artwork.rating else 0
                                        except Exception as e:
                                            print(f"❌ Error al conectar obra {artwork.title}: {str(e)}")
                                    else:
                                        print(f"⚠️ No se encontró la obra con slug: {artwork_slug}")
                                except Exception as e:
                                    print(f"Error al buscar obra {artwork_slug}: {str(e)}")
                            else:
                                print(f"⚠️ No se pudo determinar el slug de la obra")
                else:
                    print(f"⚠️ No se encontró la sala con slug: {slug}")
            except Exception as e:
                print(f"Error al procesar sala {slug}: {str(e)}")
        else:
            print(f"⚠️ No se pudo determinar el slug de la sala")
    
    # Resumen de la operación
    print(f"Resumen de la ruta creada:")
    print(f"- Salas conectadas: {rooms_connected}")
    print(f"- Paradas conectadas: {stops_connected}")
    print(f"- Obras conectadas: {artworks_connected}")
    print(f"- Valor total: {total_value}")
    
    # Actualizar el valor total y guardar
    route.total_value = total_value
    route.save()
    
    if rooms_connected == 0:
        messages.warning(request, "Se creó la ruta pero no se pudieron conectar salas. Revisa los logs.")
    else:
        messages.success(request, f"¡Ruta creada con {rooms_connected} salas y {artworks_connected} obras de arte!")
    
    return redirect('gestion_rutas:mis_rutas')

def mis_rutas_view(request):
    rutas_usuario = Route.nodes.filter(creator_username=request.user.username)
    return render(request, "mis_rutas.html", {
        "rutas": rutas_usuario
    })

def ruta_grafo_view(request, route_slug):
    try:
        if request.user.is_authenticated:
            route = Route.nodes.get(slug=route_slug, creator_username=request.user.username)
        else:
            route = Route.nodes.get(slug=route_slug, is_public=True)
    except Route.DoesNotExist:
        raise Http404(f"No Route found with slug: {route_slug}")
    except MultipleNodesReturned:
        routes = list(Route.nodes.filter(slug=route_slug))
        if routes:
            route = routes[0]
            messages.warning(request, "Se encontraron múltiples rutas con el mismo nombre.")
        else:
            raise Http404(f"No Route found with slug: {route_slug}")

    salas_visitadas = route.rooms.all()
    paradas = set(room.element_id for room in route.stops.all())

    obras_por_sala = {}
    for sala in salas_visitadas:
        if sala.element_id in paradas:
            obras_para_esta_sala = []
            for artwork in route.sees.all():
                for room in artwork.exhibited_in.all():
                    if room.element_id == sala.element_id:
                        obras_para_esta_sala.append(artwork)
                        break
            obras_por_sala[sala.element_id] = obras_para_esta_sala

    return render(request, "ver_ruta.html", {
        "route": route,
        "salas_visitadas": salas_visitadas,
        "paradas_ids": paradas,
        "obras_por_sala": obras_por_sala
    })

def safe_redirect(request, url_name, fallback_url='/'):
    """Intenta redirigir usando un nombre de URL, con fallback a URL absoluta."""
    try:
        return redirect(url_name)
    except NoReverseMatch:
        return redirect(fallback_url)

def explorar_rutas_view(request):
    # Base query - all public routes
    public_routes = Route.nodes.filter(is_public=True)
    
    # Preparar los filtros
    filters = {}
    
    # Filtrar por museo
    museum_slug = request.GET.get('museum')
    if museum_slug:
        # Filtrar rutas por museo específico
        filtered_routes = []
        for route in public_routes:
            try:
                museum = route.museum.single()
                if museum and museum.slug == museum_slug:
                    filtered_routes.append(route)
            except:
                pass  # Ignorar rutas que no tengan museo
        public_routes = filtered_routes
        filters['museum'] = museum_slug
    
    # Obtener todos los museos para el selector
    # Importar correctamente el modelo Museum
    from neomodel import db
    query = "MATCH (m:Museum) RETURN m"
    results, _ = db.cypher_query(query)
    museums = [Museum.inflate(row[0]) for row in results]
    
    # Filtrar por tiempo máximo
    max_time = request.GET.get('max_time')
    if max_time and max_time.isdigit():
        max_time_int = int(max_time)
        filtered_routes = [r for r in public_routes if r.total_time <= max_time_int]
        public_routes = filtered_routes
        filters['max_time'] = max_time
    
    # Filtrar por creador
    creator = request.GET.get('creator')
    if creator:
        filtered_routes = [r for r in public_routes if r.creator_username == creator]
        public_routes = filtered_routes
        filters['creator'] = creator
    
    # Obtener lista de creadores únicos para el filtro
    creators = list(set(route.creator_username for route in Route.nodes.filter(is_public=True)))
    
    context = {
        'routes': public_routes,
        'museums': museums,
        'creators': creators,
        'filters': filters,
        'title': 'Explorar Rutas',
    }
    
    return render(request, 'explorar_rutas.html', context)
