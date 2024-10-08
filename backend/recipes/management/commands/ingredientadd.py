import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredients


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('ingredients.json', 'rb') as f:
            data = json.load(f)
            for i in data:
                ingredient = Ingredients()
                ingredient.name = i['name']
                ingredient.measurement_unit = i['measurement_unit']
                ingredient.save()
