from django.contrib import admin

from .models import (
    Favorites,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    TagInRecipe
)
from users.mixins import DisplayEmptyFieldMixin


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
#
#
class TagInRecipeInline(admin.TabularInline):
    model = TagInRecipe
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    # inlines = (IngredientInRecipeInline,)


@admin.register(Tag)
class TagAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    # inlines = (TagInRecipeInline,)


@admin.register(Recipe)
class RecipeAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'text',
        'cooking_time',
        'pub_date',
    )
    search_fields = ('author__username', 'name',)
    list_filter = ('name', 'author', 'tags',)
    # filter_vertical = ('tags',)
    inlines = (IngredientInRecipeInline, TagInRecipeInline)


@admin.register(Favorites)
class FavoritesAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(DisplayEmptyFieldMixin, admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)
