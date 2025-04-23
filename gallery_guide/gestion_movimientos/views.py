from django.shortcuts import render
from django.http import JsonResponse, Http404
from gestion_museos.graph_models import Movement, Artwork, Museum, Artist

def lista_movimiento(request):
    """Vista para mostrar todos los movimientos artísticos disponibles"""
    movimientos = Movement.nodes.all()
    return render(request, 'lista_movimientos.html', {'movimientos': movimientos})

def obras_movimiento(request, movement_slug):
    """Vista para mostrar la página con el grafo de obras del movimiento"""
    try:
        # Obtener el movimiento usando el slug
        movement = Movement.nodes.get(slug=movement_slug)
        museums = Museum.nodes.all()
        
        # Contar las obras relacionadas con este movimiento
        # Prueba diferentes nombres de relación hasta encontrar el correcto
        try:
            # Intenta primero con 'artwork'
            obras = movement.artwork.all()
        except AttributeError:
            try:
                # Si falla, intenta con 'artworks'
                obras = movement.artworks.all()
            except AttributeError:
                # Si ambos fallan, busca obras que tengan este movimiento
                # Esta es una solución alternativa que busca la relación inversa
                obras = Artwork.nodes.filter(movement=movement)
        
        # Contar las obras
        obra_count = len(obras)
        
        # También pasamos la lista de obras para otros usos potenciales en el template
        return render(request, 'obras_movimiento.html', {
            'movement': movement,
            'museums': museums,
            'obra_count': obra_count,
            'obras': obras  # Pasar también la lista de obras
        })
    except Movement.DoesNotExist:
        raise Http404(f"No se encontró el movimiento con slug '{movement_slug}'")

def api_obras_movimiento(request, movement_slug):
    """API que devuelve los datos para generar el grafo de obras del movimiento"""
    try:
        # Obtener el movimiento usando el slug
        movement = Movement.nodes.get(slug=movement_slug)
        
        # Obtener filtros opcionales
        museum_filter = request.GET.get('museum', None)
        
        # Obtener las obras del movimiento
        artworks = movement.artworks.all()
        
        # Aplicar filtros si es necesario
        if museum_filter:
            # Filtrar obras que están en el museo seleccionado
            museum = Museum.nodes.get(name=museum_filter)
            filtered_artworks = []
            
            for artwork in artworks:
                # Buscar en qué salas está esta obra
                rooms_with_artwork = artwork.exhibited_in.all()
                
                # Verificar si alguna de esas salas pertenece al museo seleccionado
                for room in rooms_with_artwork:
                    if museum in room.museum.all():
                        filtered_artworks.append(artwork)
                        break
            
            artworks = filtered_artworks
        
        # Preparar los datos para el grafo
        nodes = []
        edges = []
        
        # Nodos de obras y sus conexiones
        for artwork in artworks:
            # Añadir nodo de la obra - solo texto plano
            tooltip = f"{artwork.title}"
            if artwork.year:
                tooltip += f"\nAño: {artwork.year}"
            if artwork.description:
                tooltip += f"\n{artwork.description}"
            
            nodes.append({
                'id': f"artwork_{artwork.slug}",
                'label': artwork.title,
                'title': tooltip,
                'group': 'artwork'
            })
            
            # Conectar obra con sus artistas (autor)
            for artist in artwork.artist.all():
                artist_id = f"artist_{artist.slug}"
                if not any(node['id'] == artist_id for node in nodes):
                    artist_tooltip = f"{artist.name}"
                    if artist.nationality:
                        artist_tooltip += f"\nNacionalidad: {artist.nationality}"
                    if artist.birth_date:
                        artist_tooltip += f"\n{artist.birth_date} - {artist.death_date or 'Presente'}"
                    
                    nodes.append({
                        'id': artist_id,
                        'label': artist.name,
                        'title': artist_tooltip,
                        'group': 'artist'
                    })
                
                edges.append({
                    'from': artist_id,
                    'to': f"artwork_{artwork.slug}",
                    'arrows': 'to',
                    'title': 'Creó'
                })
            
            # Conectar directamente obras con museos (sin nodos de sala)
            museums_added = set()
            
            for room in artwork.exhibited_in.all():
                for museum in room.museum.all():
                    # Verificar si aplicamos filtro de museo
                    if museum_filter and museum.name != museum_filter:
                        continue
                        
                    museum_id = f"museum_{museum.slug}"
                    
                    # Solo añadir museo si no lo hemos añadido antes
                    if museum_id not in museums_added:
                        museum_tooltip = f"{museum.name}"
                        if museum.location:
                            museum_tooltip += f"\nUbicación: {museum.location}"
                        
                        if not any(node['id'] == museum_id for node in nodes):
                            nodes.append({
                                'id': museum_id,
                                'label': museum.name,
                                'title': museum_tooltip,
                                'group': 'museum'
                            })
                            museums_added.add(museum_id)
                    
                    # Conectar obra directamente con museo
                    edges.append({
                        'from': f"artwork_{artwork.slug}",
                        'to': museum_id,
                        'arrows': 'to',
                        'title': 'Exhibida en'
                    })
        
        return JsonResponse({
            'nodes': nodes,
            'edges': edges
        })
    
    except Movement.DoesNotExist:
        return JsonResponse({'error': f'Movimiento con slug {movement_slug} no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
