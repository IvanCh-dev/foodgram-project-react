import json

from django.core.management.base import BaseCommand

from foodgram import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    print('Начало загрузки')

    def handle(self, *args, **options):
        path = f'{settings.BASE_DIR}/data/ingredients.json'
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for ingredient in data:
            Ingredient.objects.get_or_create(
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit'])
        print('Конец загрузки')
