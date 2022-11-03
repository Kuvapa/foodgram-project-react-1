from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from recipes.models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from recipes.serializers import (FavoritePreviewSerializer,
                                 FavoritesSerializer, IngredientSerializer,
                                 RecipeCreateSerializer, RecipeViewSerializer,
                                 TagSerializer)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrReadOnly, )
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrReadOnly, )
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeViewSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='favorite',
        permission_classes=(IsAuthenticated, ),
    )
    def set_favorite(self, request, pk=id):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite, created = Favorites.objects.get_or_create(
                recipe=recipe,
                user=self.request.user
            )
            if not created:
                return Response(
                    data={'errors': 'Рецепт уже есть в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = FavoritePreviewSerializer(favorite.recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        favorite = Favorites.objects.filter(
            user=self.request.user,
            recipe__id=pk
        )
        if not favorite.exists():
            return Response(
                {'errors': 'Рецепт не в избранном!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated, ),
    )
    def set_shopping_cart(self, request, pk=None):
        user = self.request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite = ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = FavoritesSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(ShoppingCart, user=user, recipe__id=pk)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        shopping_cart = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_total=Sum('amount')
        )
        text = 'Cписок покупок: \n'
        for ingredients in shopping_cart:
            name, measurement_unit, amount = ingredients
            text += f'{name}: {amount} {measurement_unit}\n'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping-list.txt"'
        )
        return response
