from django.core.management.base import BaseCommand
import json

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('ingredients.json', 'rb', encoding='utf-8') as f:
            data = json.load(f)
            for i in data:
                ingredient = Ingredient()
                ingredient.name = i['name']
                ingredient.measurement_unit = i['measurement_unit']
                ingredient.save()
 #               print(i['name'], i['measurement_unit'])


#
# import csv
#
# from django.core.management import BaseCommand
#
# from recipes.models import Ingredients, Tags
#
#
# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         with open('./data/ingredients.csv', encoding='utf-8') as _file:
#             reader = csv.reader(_file)
#             next(reader)
#             for row in reader:
#                 name, unit = row
#                 Ingredients.objects.get_or_create(
#                     name=name,
#                     measurement_unit=unit
#                 )
#             self.stdout.write("Ingredients import successfully")
#
#         with open('./data/tags.csv', encoding='utf-8') as file:
#             reader = csv.reader(file)
#             for row in reader:
#                 name, color, slug = row
#                 Tags.objects.get_or_create(
#                     name=name,
#                     color=color,
#                     slug=slug
#                 )
#             self.stdout.write("Tags import successfully")


# import csv
#
# from django.core.management.base import BaseCommand
#
# from recipes.models import Ingredient
#
#
# class Command(BaseCommand):
#     help = 'Добавляет ингредиенты из сsv файла в базу данных sqlite3.'
#
#     def handle(self, *args, **options):
#         with open(
#             'data/ingredients.csv',
#             'r', encoding='utf-8'
#         ) as file:
#             reader = csv.reader(file, delimiter=',')
#             Ingredient.objects.all().delete
#             for row in reader:
#                 name, unit = row
#                 Ingredient.objects.get_or_create(
#                     name=name, measurement_unit=unit)
#         print('Загрузка завершена')