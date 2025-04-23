from .graph_models import Museum, Room, Artwork, Artist, Movement, ConnectedRel
from neomodel import db
from django.utils.text import slugify

# ---------- MOVIMIENTOS ----------
def create_movements():
    print("🎨 Creando movimientos artísticos...")
    movement_data = [
        ("Renacimiento", "Movimiento cultural XV–XVI en Europa.", "1400", "1600", "Italia"),
        ("Barroco", "Estilo XVII–XVIII ornamental.", "1600", "1750", "Italia"),
        ("Neoclasicismo", "Inspirado en la antigüedad clásica.", "1750", "1850", "Francia"),
        ("Romanticismo", "Énfasis en emoción y naturaleza.", "1800", "1850", "Alemania"),
        ("Realismo", "Representa la realidad sin idealizar.", "1840", "1880", "Francia"),
        ("Impresionismo", "Captura luz y efectos cambiantes.", "1870", "1900", "Francia"),
        ("Postimpresionismo", "Estructura tras impresionismo.", "1885", "1910", "Francia"),
        ("Expresionismo", "Expresa la experiencia emocional.", "1905", "1930", "Alemania"),
        ("Cubismo", "Múltiples puntos de vista simultáneos.", "1907", "1920", "Francia"),
        ("Surrealismo", "Subconsciente onírico sin razón.", "1920", "1950", "Francia"),
        ("Arte Abstracto", "No representa realidad externa.", "1910", "1960", "Rusia"),
        ("Pop Art", "Imágenes cultura popular, producción en masa.", "1950", "1970", "Reino Unido")
    ]
    movements = {}
    for name, desc, start, end, origin in movement_data:
        movements[name] = Movement(
            name=name,
            description=desc,
            start_year=start,
            end_year=end,
            origin_country=origin
        ).save()
    return movements

# ---------- ARTISTAS ----------
def create_artists(movements):
    print("👨‍🎨 Creando artistas...")
    artist_data = [
        ("Leonardo da Vinci", "Polímata italiano del Renacimiento.", "1452", "1519", "Italiana", ["Renacimiento"]),
        ("Miguel Ángel", "Escultor y pintor renacentista.", "1475", "1564", "Italiana", ["Renacimiento"]),
        ("Rafael Sanzio", "Pintor renacentista refinado.", "1483", "1520", "Italiana", ["Renacimiento"]),
        ("Botticelli", "El nacimiento de Venus.", "1445", "1510", "Italiana", ["Renacimiento"]),
        ("Caravaggio", "Maestro del claroscuro.", "1571", "1610", "Italiana", ["Barroco"]),
        ("Diego Velázquez", "Pintor de la corte española.", "1599", "1660", "Española", ["Barroco"]),
        ("Rembrandt", "Maestro del retrato holandés.", "1606", "1669", "Holandesa", ["Barroco"]),
        ("Johannes Vermeer", "Especialista en escenas domésticas.", "1632", "1675", "Holandesa", ["Barroco"]),
        ("Jacques-Louis David", "Pintor de la revolución francesa.", "1748", "1825", "Francesa", ["Neoclasicismo"]),
        ("Francisco de Goya", "Romántico y precursor del expresionismo.", "1746", "1828", "Española", ["Romanticismo"]),
        ("Eugène Delacroix", "Romanticismo pictórico francés.", "1798", "1863", "Francesa", ["Romanticismo"]),
        ("Gustave Courbet", "Realismo crudo y directo.", "1819", "1877", "Francesa", ["Realismo"]),
        ("Claude Monet", "Pionero del impresionismo.", "1840", "1926", "Francesa", ["Impresionismo"]),
        ("Édouard Manet", "Prec. impresionismo y modernidad.", "1832", "1883", "Francesa", ["Impresionismo"]),
        ("Vincent van Gogh", "Postimpresionista atormentado.", "1853", "1890", "Holandesa", ["Postimpresionismo"]),
        ("Paul Cézanne", "Padre del arte moderno.", "1839", "1906", "Francesa", ["Postimpresionismo"]),
        ("Edvard Munch", "Expresionista noruego.", "1863", "1944", "Noruega", ["Expresionismo"]),
        ("Pablo Picasso", "Cubismo y modernidad radical.", "1881", "1973", "Española", ["Cubismo", "Surrealismo"]),
        ("Georges Braque", "Co-creador del cubismo.", "1882", "1963", "Francesa", ["Cubismo"]),
        ("Salvador Dalí", "Maestro del surrealismo.", "1904", "1989", "Española", ["Surrealismo"]),
        ("Wassily Kandinsky", "Pionero del arte abstracto.", "1866", "1944", "Rusa", ["Arte Abstracto"]),
        ("Andy Warhol", "Rey del Pop Art.", "1928", "1987", "Estadounidense", ["Pop Art"]),
        ("Roy Lichtenstein", "Cómic y arte pop.", "1923", "1997", "Estadounidense", ["Pop Art"]),
        ("Tamara de Lempicka", "Estilo art déco refinado.", "1898", "1980", "Polaca", ["Arte Abstracto"]),
        ("Joan Miró", "Surrealismo onírico y formas abstractas.", "1893", "1983", "Española", ["Surrealismo", "Arte Abstracto"]),
        ("Artemisia Gentileschi", "Pionera barroca femenina.", "1593", "1656", "Italiana", ["Barroco"]),
        ("Mary Cassatt", "Impresionista estadounidense.", "1844", "1926", "Estadounidense", ["Impresionismo"]),
        ("Frida Kahlo", "Pintora surrealista mexicana.", "1907", "1954", "Mexicana", ["Surrealismo"])
    ]
    artists = {}
    for name, bio, birth, death, nat, movs in artist_data:
        if name == 'Leonardo da Vinci':
            imagen = 'davinci.jpg'
        else:
            imagen=""
        a = Artist(
            name=name,
            bio=bio,
            birth_date=birth,
            death_date=death,
            nationality=nat,
            image=imagen
        ).save()
        for m in movs:
            a.movements.connect(movements[m])
        artists[name] = a
    return artists

# ---------- OBRAS DE ARTE ----------
def create_artworks(artists, movements):
    print("🖼️ Creando obras reales...") 
    artworks_data = [
    # RENACIMIENTO
    ("La Gioconda", "1503", "Retrato de Lisa Gherardini", "Óleo sobre tabla", "77 x 53 cm", 5, True, "Leonardo da Vinci", "Renacimiento"),
    ("La Última Cena", "1498", "Escena bíblica de la última cena", "Temple y óleo", "460 x 880 cm", 5, True, "Leonardo da Vinci", "Renacimiento"),
    ("El Hombre de Vitruvio", "1490", "Estudio de proporciones", "Tinta sobre papel", "34 x 25 cm", 4, False, "Leonardo da Vinci", "Renacimiento"),
    ("La creación de Adán", "1512", "Dios da vida a Adán", "Fresco", "280 x 570 cm", 5, True, "Miguel Ángel", "Renacimiento"),
    ("El Juicio Final", "1541", "Fresco de la Capilla Sixtina", "Fresco", "1370 x 1220 cm", 5, True, "Miguel Ángel", "Renacimiento"),
    ("La escuela de Atenas", "1511", "Filosofía clásica", "Fresco", "500 x 770 cm", 5, True, "Rafael Sanzio", "Renacimiento"),
    ("El nacimiento de Venus", "1485", "Venus sobre concha marina", "Temple sobre lienzo", "172 x 278 cm", 5, True, "Botticelli", "Renacimiento"),
    ("La primavera", "1482", "Alegoría mitológica", "Temple sobre tabla", "203 x 314 cm", 4, True, "Botticelli", "Renacimiento"),
    # BARROCO
    ("Las meninas", "1656", "Retrato de la infanta Margarita", "Óleo sobre lienzo", "318 x 276 cm", 5, True, "Diego Velázquez", "Barroco"),
    ("La rendición de Breda", "1634", "Conquista de Breda", "Óleo sobre lienzo", "307 x 367 cm", 5, True, "Diego Velázquez", "Barroco"),
    ("La vocación de San Mateo", "1600", "Llamado de Mateo", "Óleo sobre lienzo", "322 x 340 cm", 4, True, "Caravaggio", "Barroco"),
    ("Judith decapitando a Holofernes", "1599", "Escena bíblica", "Óleo sobre lienzo", "145 x 195 cm", 4, False, "Caravaggio", "Barroco"),
    ("La ronda de noche", "1642", "Milicia neerlandesa", "Óleo sobre lienzo", "363 x 437 cm", 5, True, "Rembrandt", "Barroco"),
    ("La joven de la perla", "1665", "Retrato enigmático", "Óleo sobre lienzo", "44.5 x 39 cm", 5, True, "Johannes Vermeer", "Barroco"),
    # NEOCLASICISMO
    ("La muerte de Marat", "1793", "Martirio de Marat", "Óleo sobre lienzo", "165 x 128 cm", 4, True, "Jacques-Louis David", "Neoclasicismo"),
    ("El Juramento de los Horacios", "1784", "Deber y sacrificio", "Óleo sobre lienzo", "330 x 425 cm", 5, True, "Jacques-Louis David", "Neoclasicismo"),
    # ROMANTICISMO
    ("Los fusilamientos del 3 de mayo", "1814", "Represalias napoleónicas", "Óleo sobre lienzo", "268 x 347 cm", 5, True, "Francisco de Goya", "Romanticismo"),
    ("Saturno devorando a su hijo", "1823", "Furia mitológica", "Óleo sobre muro", "143 x 81 cm", 4, False, "Francisco de Goya", "Romanticismo"),
    ("La libertad guiando al pueblo", "1830", "Revolución francesa", "Óleo sobre lienzo", "260 x 325 cm", 5, True, "Eugène Delacroix", "Romanticismo"),
    # REALISMO
    ("El entierro en Ornans", "1850", "Funeral en Ornans", "Óleo sobre lienzo", "315 x 668 cm", 4, False, "Gustave Courbet", "Realismo"),
    # IMPRESIONISMO
    ("Impresión, sol naciente", "1872", "Puerto de Le Havre", "Óleo sobre lienzo", "48 x 63 cm", 5, True, "Claude Monet", "Impresionismo"),
    ("Nenúfares", "1916", "Estanque de Giverny", "Óleo sobre lienzo", "200 x 200 cm", 5, False, "Claude Monet", "Impresionismo"),
    ("La catedral de Ruan", "1894", "Serie impresionista", "Óleo sobre lienzo", "100 x 65 cm", 4, False, "Claude Monet", "Impresionismo"),
    ("Le déjeuner sur l'herbe", "1863", "Picnic escandaloso", "Óleo sobre lienzo", "208 x 264.5 cm", 5, True, "Édouard Manet", "Impresionismo"),
    # POSTIMPRESIONISMO
    ("La noche estrellada", "1889", "Cielo nocturno expresivo", "Óleo sobre lienzo", "73.7 x 92.1 cm", 5, True, "Vincent van Gogh", "Postimpresionismo"),
    ("Los girasoles", "1888", "Naturaleza viva", "Óleo sobre lienzo", "92 x 73 cm", 5, False, "Vincent van Gogh", "Postimpresionismo"),
    ("Autorretrato con oreja vendada", "1889", "Retrato psicológico", "Óleo sobre lienzo", "60 x 49 cm", 4, False, "Vincent van Gogh", "Postimpresionismo"),
    ("Los jugadores de cartas", "1895", "Serie de campesinos", "Óleo sobre lienzo", "47.5 x 57 cm", 4, False, "Paul Cézanne", "Postimpresionismo"),
    # EXPRESIONISMO
    ("El grito", "1893", "Angustia moderna", "Óleo y pastel sobre cartón", "91 x 73.5 cm", 5, True, "Edvard Munch", "Expresionismo"),
    # CUBISMO
    ("Guernica", "1937", "Bombardeo en Guernica", "Óleo sobre lienzo", "349.3 x 776.6 cm", 5, True, "Pablo Picasso", "Cubismo"),
    ("Las señoritas de Avignon", "1907", "Desnudos angulosos", "Óleo sobre lienzo", "243.9 x 233.7 cm", 5, True, "Pablo Picasso", "Cubismo"),
    ("Violín y candelabro", "1910", "Objetos fragmentados", "Óleo sobre lienzo", "61 x 50 cm", 4, False, "Georges Braque", "Cubismo"),
     # SURREALISMO
    ("La persistencia de la memoria", "1931", "Relojes blandos", "Óleo sobre lienzo", "24 x 33 cm", 5, True, "Salvador Dalí", "Surrealismo"),
    ("Las dos Fridas", "1939", "Dualidad emocional", "Óleo sobre lienzo", "173 x 173 cm", 5, False, "Frida Kahlo", "Surrealismo"),
    # ABSTRACTO
    ("Composición VIII", "1923", "Formas geométricas", "Óleo sobre lienzo", "140 x 201 cm", 4, False, "Wassily Kandinsky", "Arte Abstracto"),
    # POP ART
    ("Campbell's Soup Cans", "1962", "Latas de sopa", "Acrílico sobre lienzo", "51 x 41 cm", 5, True, "Andy Warhol", "Pop Art"),
    ("Marilyn Diptych", "1962", "Retrato repetido", "Serigrafía", "205 x 289 cm", 5, True, "Andy Warhol", "Pop Art"),
    ("Whaam!", "1963", "Viñeta explosiva", "Acrílico sobre lienzo", "172 x 406 cm", 4, False, "Roy Lichtenstein", "Pop Art"),
    ("Girl with Ball", "1961", "Figura femenina pop", "Acrílico sobre lienzo", "152 x 152 cm", 3, False, "Roy Lichtenstein", "Pop Art")
    ]

    artworks = []
    for title, year, desc, medium, dimensions, rating, masterpiece, artist_name, movement_name in artworks_data:
        artwork = Artwork(
            title=title,
            slug=slugify(title),  # Crear slug a partir del título
            year=year,
            description=desc,
            medium=medium,
            dimensions=dimensions,
            rating=rating,
            masterpiece=masterpiece,
            image=""
        ).save()
        artwork.artist.connect(artists[artist_name])
        artwork.movement.connect(movements[movement_name])
        artworks.append(artwork)
    return artworks

# ---------- MUSEOS Y SALAS ----------
def create_museums_and_rooms(artworks):
    print("🏛️ Creando museos y asignando obras...")

    base_dists = [10, 12, 8, 15, 9, 11, 7, 13, 14, 6]
    base_times = [2, 3, 1, 2, 3]
    dist_idx = 0

    def connect_rooms(prev, current):
        nonlocal dist_idx
        rel = prev.connected_to.connect(current)
        rel.distance = base_dists[dist_idx % len(base_dists)]
        rel.transit_time = base_times[dist_idx % len(base_times)]
        rel.save()
        dist_idx += 1

    def create_floor_rooms(museum, floor_index, num_rooms, name_prefix, entrance=False, exit=False, themes=None):
        rooms = []
        for i in range(num_rooms):
            is_ent = entrance and i == 0
            is_ex = exit and i == num_rooms - 1
            theme = themes[i] if themes else ""
            room_name = f"{name_prefix}.{i+1}"
            room_slug = slugify(room_name)  # Crear slug a partir del nombre
            
            r = Room(
                name=room_name,
                slug=room_slug,  # Asignar slug aquí
                floor=floor_index,
                is_entrance=is_ent,
                is_exit=is_ex,
                theme=theme,
                description="Sala expositiva",
                image=""
            ).save()
            museum.rooms.connect(r)
            rooms.append(r)
        return rooms

    remaining_artworks = artworks.copy()

    def assign_artworks_to_rooms(room_list, artworks_per_room):
        for room in room_list:
            for _ in range(artworks_per_room):
                if remaining_artworks:
                    room.artworks.connect(remaining_artworks.pop(0))

    # MUSEOS
    m1 = Museum(name="Museo de los Movimientos", location="Madrid", description="Obras clasificadas por movimientos", foundation_year="1930", floors=2, image="").save()
    m2 = Museum(name="Museo Maestros del Arte", location="Barcelona", description="Obras de autores célebres", foundation_year="1940", floors=2, image="").save()
    m3 = Museum(name="Museo Cronológico", location="Valencia", description="Un paseo por los siglos", foundation_year="1955", floors=3, image="").save()
    m4 = Museum(name="Galería Universal", location="Sevilla", description="Obras variadas sin criterio específico", foundation_year="1970", floors=1, image="").save()

    # Salas y asignaciones
    themes1 = ["Renacimiento", "Barroco", "Impresionismo", "Cubismo", "Surrealismo", "Pop Art"]
    r1 = create_floor_rooms(m1, 0, 3, "Movimientos - Sala 0", entrance=True, themes=themes1[:3])
    r1 += create_floor_rooms(m1, 1, 3, "Movimientos - Sala 1", exit=True, themes=themes1[3:])
    for i in range(len(r1)-1): connect_rooms(r1[i], r1[i+1])
    assign_artworks_to_rooms(r1, 3)

    themes2 = ["Leonardo da Vinci", "Miguel Ángel", "Velázquez", "Van Gogh", "Monet", "Picasso"]
    r2 = create_floor_rooms(m2, 0, 3, "Maestros - Sala 0", entrance=True, themes=themes2[:3])
    r2 += create_floor_rooms(m2, 1, 3, "Maestros - Sala 1", exit=True, themes=themes2[3:])
    for i in range(len(r2)-1): connect_rooms(r2[i], r2[i+1])
    assign_artworks_to_rooms(r2, 3)

    themes3 = ["Siglo XV-XVI", "Siglo XVII", "Siglo XVIII", "Siglo XIX", "Siglo XX"]
    r3 = create_floor_rooms(m3, 0, 2, "Crono - Sala 0", entrance=True, themes=themes3[:2])
    r3 += create_floor_rooms(m3, 1, 2, "Crono - Sala 1", themes=themes3[2:4])
    r3 += create_floor_rooms(m3, 2, 1, "Crono - Sala 2", exit=True, themes=themes3[4:])
    for i in range(len(r3)-1): connect_rooms(r3[i], r3[i+1])
    assign_artworks_to_rooms(r3, 3)

    themes4 = ["Clásicos", "Modernos", "Contemporáneos"]
    r4 = create_floor_rooms(m4, 0, 3, "Mixto - Sala 0", entrance=True, exit=True, themes=themes4)
    for i in range(len(r4)-1):
        connect_rooms(r4[i], r4[i+1])

    # Aseguramos que se usen todas las obras restantes
    num_salas = len(r4)
    num_obras_restantes = len(remaining_artworks)
    print(f"🎯 Asignando {num_obras_restantes} obras a Galería Universal...")

    for i, obra in enumerate(remaining_artworks):
        r4[i % num_salas].artworks.connect(obra)

    # Verificación opcional de cuántas obras recibe cada sala (puedes quitar luego)
    for sala in r4:
        obras_en_sala = sala.artworks.all()
        print(f"🖼️ Sala '{sala.name}' contiene {len(obras_en_sala)} obras.")

        print("✅ Museos creados y obras asignadas correctamente.")

# ---------- FUNCIÓN GLOBAL ----------
def populate_sample_data():
    print("🧹 Limpiando base de datos Neo4j...")
    db.cypher_query("MATCH (n) DETACH DELETE n")
    movements = create_movements()
    artists = create_artists(movements)
    artworks = create_artworks(artists, movements)
    create_museums_and_rooms(artworks)
    print("🏁 Población de datos estáticos completa.")