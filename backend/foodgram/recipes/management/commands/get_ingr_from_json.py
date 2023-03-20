import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    print('Начало загрузки')

    def handle(self, *args, **options):
        with open('D:\\Dev\\foodgram-project-react\\data\\ingredients.json',
                  'r', encoding='utf-8') as f:
            data = json.load(f)
        for ingredient in data:
            Ingredient.objects.get_or_create(
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit'])
        print('Конец загрузки')
