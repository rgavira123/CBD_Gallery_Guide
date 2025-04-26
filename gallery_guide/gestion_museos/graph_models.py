from neomodel import (
    StructuredNode, StringProperty, DateProperty, 
    IntegerProperty, BooleanProperty, FloatProperty,
    RelationshipTo, RelationshipFrom, StructuredRel
)
from django.utils.text import slugify  # Importa slugify para generar slugs
import sys

# Check if this module is already loaded to prevent redefining classes
if 'gestion_museos.graph_models.Museum' in sys.modules:
    # If already loaded, get the existing classes from sys.modules
    Museum = sys.modules['gestion_museos.graph_models.Museum']
    Room = sys.modules['gestion_museos.graph_models.Room']
    Artwork = sys.modules['gestion_museos.graph_models.Artwork']
    Artist = sys.modules['gestion_museos.graph_models.Artist']
    Movement = sys.modules['gestion_museos.graph_models.Movement']
else:
    # Definición de relación estructurada para las conexiones entre salas
    class ConnectedRel(StructuredRel):
        transit_time = IntegerProperty(default=5)  # Tiempo en minutos para ir de una sala a otra
    
    # Relación estructurada para las exhibiciones de obras
    class ExhibitsRel(StructuredRel):
        position = StringProperty(default="center")  # Posición de la obra en la sala
    
    # Relación estructurada para la relación entre museo y sala
    class HasRoomRel(StructuredRel):
        # Puedes añadir propiedades si las necesitas
        order = IntegerProperty(default=0)  # Orden de la sala en el museo
    
    class Museum(StructuredNode):
        name = StringProperty(required=True, unique_index=True)
        slug = StringProperty(unique_index=True)
        description = StringProperty(default="")
        location = StringProperty(default="")
        foundation_year = IntegerProperty(default=0)
        floors = IntegerProperty(default=1)
        
        # Relaciones
        rooms = RelationshipTo('Room', 'HAS_ROOM', model=HasRoomRel)
        
        def save(self, *args, **kwargs):
            # Genera el slug automáticamente basado en el nombre
            if not self.slug:
                self.slug = slugify(self.name)
            super().save(*args, **kwargs)
            return self
    
    class Room(StructuredNode):
        name = StringProperty(required=True)
        slug = StringProperty(unique_index=True)
        description = StringProperty(default="")
        floor = IntegerProperty(default=0)
        is_entrance = BooleanProperty(default=False)
        is_exit = BooleanProperty(default=False)
        theme = StringProperty(default="")
        transit_time = IntegerProperty(default=5)
        
        # Relaciones
        connected_to = RelationshipTo('Room', 'CONNECTED_TO', model=ConnectedRel)
        artworks = RelationshipTo('Artwork', 'EXHIBITS', model=ExhibitsRel)
        museum = RelationshipFrom('Museum', 'HAS_ROOM', model=HasRoomRel)
    
        def save(self, *args, **kwargs):
            # Genera el slug automáticamente basado en el nombre
            if not self.slug:
                self.slug = slugify(self.name)
            super().save(*args, **kwargs)
            return self
    
    class Artwork(StructuredNode):
        title = StringProperty(required=True)
        slug = StringProperty(unique_index=True)
        year = IntegerProperty(default=0)
        description = StringProperty(default="")
        medium = StringProperty(default="")
        dimensions = StringProperty(default="")
        image = StringProperty(default="")
        rating = IntegerProperty(default=3)  # Valoración de 1 a 5
        masterpiece = BooleanProperty(default=False)  # Indica si es una obra maestra
        
        # Relaciones
        artist = RelationshipTo('Artist', 'CREATED_BY')
        movement = RelationshipTo('Movement', 'BELONGS_TO')
        exhibited_in = RelationshipFrom('Room', 'EXHIBITS', model=ExhibitsRel)
        
        def save(self, *args, **kwargs):
            # Genera el slug automáticamente basado en el título
            if not self.slug:
                self.slug = slugify(self.title)
            super().save(*args, **kwargs)
            return self
    
    class Artist(StructuredNode):
        name = StringProperty(required=True)
        slug = StringProperty(unique_index=True)
        nationality = StringProperty(default="")
        birth_date = StringProperty(default="")
        death_date = StringProperty(default="")
        bio = StringProperty(default="")
        image = StringProperty(default="")
        
        # Relaciones
        artworks = RelationshipFrom('Artwork', 'CREATED_BY')
        movements = RelationshipTo('Movement', 'PART_OF')
        
        def save(self, *args, **kwargs):
            # Genera el slug automáticamente basado en el nombre
            if not self.slug:
                self.slug = slugify(self.name)
            super().save(*args, **kwargs)
            return self
    
    class Movement(StructuredNode):
        name = StringProperty(required=True)
        slug = StringProperty(unique_index=True)
        description = StringProperty(default="")
        start_year = IntegerProperty(default=0)
        end_year = IntegerProperty(default=0)
        origin_country = StringProperty(default="")
        
        # Relaciones
        artworks = RelationshipFrom('Artwork', 'BELONGS_TO')
        artists = RelationshipFrom('Artist', 'PART_OF')
        
        def save(self, *args, **kwargs):
            # Genera el slug automáticamente basado en el nombre
            if not self.slug:
                self.slug = slugify(self.name)
            super().save(*args, **kwargs)
            return self