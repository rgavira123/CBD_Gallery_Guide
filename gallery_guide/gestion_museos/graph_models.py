from neomodel import StructuredNode, StringProperty, RelationshipTo

class Movement(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    description = StringProperty()

class Artist(StructuredNode):
    name = StringProperty(required=True)
    bio = StringProperty()
    movements = RelationshipTo('Movement', 'ASSOCIATED_WITH')

class Artwork(StructuredNode):
    title = StringProperty(required=True)
    year = StringProperty()
    description = StringProperty()
    artist = RelationshipTo('Artist', 'CREATED_BY')
    movement = RelationshipTo('Movement', 'BELONGS_TO')

class Room(StructuredNode):
    name = StringProperty(required=True)
    description = StringProperty()
    connected_to = RelationshipTo('Room', 'CONNECTED_TO')
    artworks = RelationshipTo('Artwork', 'HAS_ARTWORK')

class Museum(StructuredNode):
    name = StringProperty(required=True, unique_index=True)
    location = StringProperty()
    rooms = RelationshipTo(Room, 'HAS_ROOM')
