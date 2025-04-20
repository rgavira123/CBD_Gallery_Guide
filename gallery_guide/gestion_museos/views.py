from django.http import JsonResponse
from django.shortcuts import render
from .graph_models import *

def museum_graph_view(request, museum_name):
    try:
        museum = Museum.nodes.get(name=museum_name)
        rooms = museum.rooms.all()
        connections = []
        for room in rooms:
            for connected_room in room.connected_to:
                connections.append((room.name, connected_room.name))
        return render(request, 'museum_graph.html', {
            'museum': museum,
            'rooms': rooms,
            'connections': connections
        })
    except Museum.DoesNotExist:
        return render(request, 'museum_graph.html', {'error': 'Museum not found'})

def obras_por_sala(request, room_name):
    try:
        room = Room.nodes.get(name=room_name)
        artworks = room.artworks.all()

        nodes = []
        edges = []

        for artwork in artworks:
            # Nodo de la obra
            nodes.append({
                'id': artwork.title,
                'label': artwork.title,
                'title': f"Autor: {artwork.artist.all()[0].name}" if artwork.artist else "Autor desconocido",
                'group': 'artwork'
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
            'edges': edges
        })

    except Room.DoesNotExist:
        return JsonResponse({'error': 'Sala no encontrada'}, status=404)