from django.http import JsonResponse
from django.shortcuts import render
from .graph_models import *
import networkx as nx

def listar_museos(request):
    """Vista para mostrar todos los museos disponibles en tarjetas."""
    museos = Museum.nodes.all()
    museos_con_tiempos = []
    
    for museo in museos:
        # Calculamos el tiempo total para ver el museo completo
        tiempo_total_minutos = calcular_tiempo_total_museo(museo)
        
        # Añadimos el tiempo al objeto museo (como atributo dinámico)
        museo.tiempo_total = tiempo_total_minutos
        museos_con_tiempos.append(museo)
        
    return render(request, 'museos.html', {'museos': museos_con_tiempos})

def calcular_tiempo_total_museo(museo):
    """Calcula el tiempo total en minutos para ver todo el museo."""
    total_minutos = 0
    rooms = museo.rooms.all()
    
    # Creamos un grafo para calcular la ruta más corta
    G = nx.DiGraph()
    
    # Añadimos todas las salas al grafo
    for room in rooms:
        # Calculamos el tiempo de visita de cada sala
        tiempo_sala = calcular_tiempo_sala(room)
        G.add_node(room.name, tiempo_visita=tiempo_sala)
        total_minutos += tiempo_sala
    
    # Añadimos las conexiones entre salas
    for room in rooms:
        for connected_room in room.connected_to:
            # Obtenemos la relación para acceder a sus propiedades
            rel = room.connected_to.relationship(connected_room)
            transit_time = rel.transit_time
            G.add_edge(room.name, connected_room.name, tiempo_transito=transit_time)
            total_minutos += transit_time
    
    # Bonus: si hay entrada y salida, podríamos calcular la ruta óptima
    # Pero como es un museo completo, simplemente sumamos todos los tiempos
    
    return total_minutos

def calcular_tiempo_sala(sala):
    """Calcula el tiempo en minutos para ver una sala."""
    artworks = sala.artworks.all()
    tiempo_minutos = 0
    
    for artwork in artworks:
        if artwork.masterpiece:
            # Obras maestras: 5 minutos
            tiempo_minutos += 5
        else:
            # Obras normales: 30 segundos = 0.5 minutos
            tiempo_minutos += 0.5
    
    # Redondeamos al siguiente minuto completo
    return round(tiempo_minutos)

def museum_graph_view(request, museum_slug):
    try:
        museum = Museum.nodes.get(slug=museum_slug)
        rooms = museum.rooms.all()

        # Añadimos cálculos de tiempo para cada sala
        for room in rooms:
            room.tiempo_visita = calcular_tiempo_sala(room)

        connections = []
        for room in rooms:
            for connected_room in room.connected_to:
                rel = room.connected_to.relationship(connected_room)
                connections.append((
                    room.name,  # Usar name en lugar de slug
                    connected_room.name,  # Usar name en lugar de slug
                    rel.transit_time
                ))

        tiempo_total = calcular_tiempo_total_museo(museum)
        floors = set(room.floor for room in rooms)
        floors_range = sorted(floors)

        return render(request, 'museum_graph.html', {
            'museum': museum,
            'rooms': rooms,
            'connections': connections,
            'tiempo_total': tiempo_total,
            'floors_range': floors_range
        })
    except Museum.DoesNotExist:
        return render(request, 'error.html', {'error_message': 'Museo no encontrado.'})

def obras_por_sala(request, room_name):
    try:
        room = Room.nodes.get(name=room_name)
        artworks = room.artworks.all()
        
        # Cálculo del tiempo de visita para la sala
        tiempo_visita = calcular_tiempo_sala(room)

        nodes = []
        edges = []

        for artwork in artworks:
            # Definimos el grupo según sea masterpiece o no
            artwork_group = 'masterpiece' if artwork.masterpiece else 'artwork'
            
            # Nodo de la obra
            nodes.append({
                'id': artwork.title,
                'label': artwork.title,
                'title': f"Autor: {artwork.artist.all()[0].name if artwork.artist else 'Desconocido'}\nTiempo: {'5 min' if artwork.masterpiece else '30 seg'}",
                'group': artwork_group
            })

            # Corriente artística
            movement = artwork.movement.all()
            if movement:
                mov = movement[0]
                nodes.append({
                    'id': f"mov_{mov.name}",
                    'label': mov.name,
                    'title': mov.description,
                    'group': 'movement'
                })
                edges.append({
                    'from': artwork.title,
                    'to': f"mov_{mov.name}"
                })

        return JsonResponse({
            'nodes': nodes,
            'edges': edges,
            'tiempo_visita': tiempo_visita
        })

    except Room.DoesNotExist:
        return JsonResponse({'error': 'Sala no encontrada'}, status=404)

def room_artworks_view(request, museum_slug, room_name):
    try:
        museum = Museum.nodes.get(slug=museum_slug)
        room = Room.nodes.get(name=room_name)
        
        # Verificar que la sala pertenece al museo
        rooms_in_museum = museum.rooms.all()
        museum_room_names = [r.name for r in rooms_in_museum]
        
        if room.name not in museum_room_names:
            return render(request, 'error.html', {
                'error_message': f'La sala "{room.name}" no pertenece al museo "{museum.name}".'
            })
        
        # Obtener todas las obras en la sala
        artworks = room.artworks.all()
        
        # Calcular el tiempo de visita
        room.tiempo_visita = calcular_tiempo_sala(room)
        
        # Obtener la obra seleccionada (si existe en los parámetros)
        selected_artwork_id = request.GET.get('artwork')
        selected_artwork = None
        if selected_artwork_id:
            for artwork in artworks:
                if str(artwork.element_id) == selected_artwork_id:
                    selected_artwork = artwork
                    break
        
        return render(request, 'room_artworks.html', {
            'museum': museum,
            'room': room,
            'artworks': artworks,
            'selected_artwork': selected_artwork
        })
    
    except Museum.DoesNotExist:
        return render(request, 'error.html', {
            'error_message': f'El museo con slug "{museum_slug}" no existe.'
        })
    except Room.DoesNotExist:
        return render(request, 'error.html', {
            'error_message': f'La sala con nombre "{room_name}" no existe.'
        })
    except Exception as e:
        return render(request, 'error.html', {
            'error_message': f'Error inesperado: {str(e)}'
        })

def artwork_detail(request, artwork_id):
    try:
        artwork = Artwork.nodes.get(id=artwork_id)
        
        # Formato para JSON
        artist = artwork.artist.single() if artwork.artist else None
        movement = artwork.movement.single() if artwork.movement else None
        
        return JsonResponse({
            'id': artwork.id,
            'title': artwork.title,
            'year': artwork.year,
            'description': artwork.description,
            'medium': artwork.medium,
            'dimensions': artwork.dimensions,
            'rating': artwork.rating,
            'masterpiece': artwork.masterpiece,
            'image': artwork.image,
            'artist_name': artist.name if artist else "Desconocido",
            'artist_id': artist.id if artist else None,
            'movement_name': movement.name if movement else "No especificado",
            'movement_id': movement.id if movement else None,
        })
    except Artwork.DoesNotExist:
        return JsonResponse({'error': 'Artwork not found'}, status=404)