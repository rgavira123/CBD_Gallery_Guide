from django.core.management.base import BaseCommand
from gestion_museos.graph_models import Museum
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Genera slugs para los museos existentes'

    def handle(self, *args, **kwargs):
        museums = Museum.nodes.all()
        for museum in museums:
            if not museum.slug:
                museum.slug = slugify(museum.name)
                museum.save()
                self.stdout.write(self.style.SUCCESS(f'Slug generado para {museum.name}: {museum.slug}'))