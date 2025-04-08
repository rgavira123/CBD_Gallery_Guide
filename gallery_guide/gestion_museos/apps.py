from django.apps import AppConfig
from neomodel import config as neo4j_config
from django.conf import settings

class GestionMuseosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_museos'
    
    def ready(self):
        neo4j_config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
