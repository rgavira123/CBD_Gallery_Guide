from neomodel import (
    StructuredNode, StringProperty, DateProperty, 
    IntegerProperty, BooleanProperty, FloatProperty,
    RelationshipTo, RelationshipFrom, StructuredRel
)

# Definición de relación estructurada para las conexiones entre salas
class ConnectedRel(StructuredRel):
    distance = IntegerProperty(default=10)  # Distancia en metros
    transit_time = IntegerProperty(default=2)  # Tiempo en minutos

# Resto de definiciones de modelos
class Museum(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    location = StringProperty(required=True)
    description = StringProperty(default="")
    foundation_year = StringProperty()
    floors = IntegerProperty(default=1)
    image = StringProperty()  # Imagen en base64

    rooms = RelationshipTo('Room', 'HAS_ROOM')

class Room(StructuredNode):
    name = StringProperty(required=True)
    description = StringProperty(default="")
    floor = IntegerProperty(default=0)
    is_entrance = BooleanProperty(default=False)
    is_exit = BooleanProperty(default=False)
    theme = StringProperty(default="")
    transit_time = IntegerProperty(default=5)  # Tiempo estimado para ver la sala (minutos)
    
    # Relaciones
    connected_to = RelationshipTo('Room', 'CONNECTED_TO', model=ConnectedRel)
    artworks = RelationshipTo('Artwork', 'EXHIBITS')
    museum = RelationshipFrom('Museum', 'HAS_ROOM')

class Artwork(StructuredNode):
    title = StringProperty(required=True)
    year = StringProperty()
    description = StringProperty(default="")
    medium = StringProperty(default="")
    dimensions = StringProperty(default="")
    rating = IntegerProperty(default=3)
    masterpiece = BooleanProperty(default=False)
    image = StringProperty()  # Imagen en base64

    artist = RelationshipTo('Artist', 'CREATED_BY')
    movement = RelationshipTo('Movement', 'BELONGS_TO')
    exhibited_in = RelationshipFrom('Room', 'EXHIBITS')

class Artist(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    image = StringProperty()  # Esto debería contener solo el nombre del archivo, no la ruta completa
    bio = StringProperty(default="")
    birth_date = StringProperty()
    death_date = StringProperty()
    nationality = StringProperty()

    artworks = RelationshipFrom('Artwork', 'CREATED_BY')
    movements = RelationshipTo('Movement', 'PART_OF')

    # Puedes añadir este método para obtener la URL completa si es necesario
    def get_image_url(self):
        if self.image:
            return f"images/autores/{self.image}"
        return None

class Movement(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    description = StringProperty(default="")
    start_year = StringProperty()
    end_year = StringProperty()
    origin_country = StringProperty()
    
    # Relaciones
    artworks = RelationshipFrom('Artwork', 'BELONGS_TO')
    artists = RelationshipFrom('Artist', 'PART_OF')
