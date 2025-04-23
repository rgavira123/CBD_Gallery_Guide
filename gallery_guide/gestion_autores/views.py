from django.shortcuts import render
from django.http import JsonResponse, Http404
from gestion_museos.graph_models import Artist, Artwork, Museum

def lista_autores(request):
    # Obtener todos los artistas de Neo4j
    artistas = Artist.nodes.all()
    return render(request, 'lista_autores.html', {'artistas': artistas})

def obras_autor(request, author_slug):
    """Vista para mostrar la página con el grafo de obras del autor"""
    try:
        # Obtener el artista usando el slug
        author = Artist.nodes.get(slug=author_slug)
        museums = Museum.nodes.all()
        return render(request, 'obras_autor.html', {
            'author': author,
            'museums': museums
        })
    except Artist.DoesNotExist:
        raise Http404(f"No se encontró el artista con slug '{author_slug}'")

def api_obras_autor(request, author_slug):
    """API que devuelve los datos para generar el grafo de obras del autor"""
    try:
        # Obtener el artista usando el slug
        artist = Artist.nodes.get(slug=author_slug)
        
        # Obtener filtros opcionales
        museum_filter = request.GET.get('museum', None)
        
        # Obtener las obras del artista
        artworks = artist.artworks.all()
        
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
            
            # Conectar obra con su movimiento
            for movement in artwork.movement.all():
                movement_id = f"movement_{movement.slug}"
                if not any(node['id'] == movement_id for node in nodes):
                    movement_tooltip = f"{movement.name}"
                    if movement.description:
                        movement_tooltip += f"\n{movement.description}"
                    
                    nodes.append({
                        'id': movement_id,
                        'label': movement.name,
                        'title': movement_tooltip,
                        'group': 'movement'
                    })
                
                edges.append({
                    'from': f"artwork_{artwork.slug}",
                    'to': movement_id,
                    'arrows': 'to',
                    'title': 'Pertenece a'
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
    
    except Artist.DoesNotExist:
        return JsonResponse({'error': f'Artista con slug {author_slug} no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
