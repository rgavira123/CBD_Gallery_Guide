from django.core.management.base import BaseCommand
from gestion_museos.sample_graph_data import populate_sample_data

class Command(BaseCommand):
    help = 'Popula la base de datos Neo4j con datos de muestra para el proyecto Gallery Guide'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de datos en Neo4j...'))
        populate_sample_data()
        self.stdout.write(self.style.SUCCESS('¡Datos cargados exitosamente!'))