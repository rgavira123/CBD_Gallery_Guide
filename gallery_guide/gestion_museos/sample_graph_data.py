from .graph_models import Museum, Room, Artwork, Artist, Movement

def populate_sample_data():
    from neomodel import db
    db.cypher_query("MATCH (n) DETACH DELETE n")  # Solo para testing: borra todo

    # Movimientos
    cubismo = Movement(name="Cubismo", description="Movimiento artístico del siglo XX que rompe con la perspectiva tradicional.").save()
    impresionismo = Movement(name="Impresionismo", description="Movimiento que busca capturar la luz y el instante.").save()

    # Artistas
    picasso = Artist(name="Pablo Picasso", bio="Pintor español, uno de los creadores del cubismo.").save()
    monet = Artist(name="Claude Monet", bio="Pintor francés, padre del impresionismo.").save()

    # Asignar movimientos a artistas
    picasso.movements.connect(cubismo)
    monet.movements.connect(impresionismo)

    # Obras
    guernica = Artwork(title="Guernica", year="1937", description="Obra antibélica sobre el bombardeo de Guernica.").save()
    nenufares = Artwork(title="Nenúfares", year="1916", description="Paisaje acuático impresionista.").save()

    # Relacionar obras con artistas y movimientos
    guernica.artist.connect(picasso)
    guernica.movement.connect(cubismo)

    nenufares.artist.connect(monet)
    nenufares.movement.connect(impresionismo)

    # Museo y salas
    museo = Museum(name="Museo Moderno", location="Madrid").save()
    sala_a = Room(name="Sala A", description="Arte contemporáneo").save()
    sala_b = Room(name="Sala B", description="Impresionismo").save()

    museo.rooms.connect(sala_a)
    museo.rooms.connect(sala_b)

    sala_a.connected_to.connect(sala_b)

    # Añadir obras a salas
    sala_a.artworks.connect(guernica)
    sala_b.artworks.connect(nenufares)

    print("📊 Datos de prueba COMPLETOS creados con éxito")
