from neomodel import (
    StructuredNode, StringProperty, IntegerProperty, BooleanProperty,
    DateTimeProperty, RelationshipTo
)
from django.utils.text import slugify

class Route(StructuredNode):
    name = StringProperty(required=True)
    slug = StringProperty(unique_index=True)
    description = StringProperty(default="")
    created_at = DateTimeProperty(default_now=True)
    total_time = IntegerProperty(required=True)
    total_value = IntegerProperty(required=True)
    is_public = BooleanProperty(default=False)
    creator_username = StringProperty(required=True)

    # Relaciones
    museum = RelationshipTo('gestion_museos.graph_models.Museum', 'BELONGS_TO')
    rooms = RelationshipTo('gestion_museos.graph_models.Room', 'VISITS')  # Todas las salas recorridas
    stops = RelationshipTo('gestion_museos.graph_models.Room', 'STOPS_AT')  # Salas de parada real
    sees = RelationshipTo('gestion_museos.graph_models.Artwork', 'SEES')  # Obras que ve en la ruta

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        return self
