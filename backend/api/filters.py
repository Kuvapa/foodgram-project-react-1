from django_filters import rest_framework
from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug'
    )
    is_favorited = rest_framework.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(
                favorite_recipe__user=self.request.user
            )
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(shopping_cart__user=self.request.user)
        return Recipe.objects.all()


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')
