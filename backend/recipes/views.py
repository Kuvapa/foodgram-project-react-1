from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from recipes.models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from recipes.serializers import (FavoritesSerializer, IngredientSerializer,
                                 RecipeCreateSerializer, RecipeViewSerializer,
                                 ShoppingCartSerializer, TagSerializer)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeViewSerializer
        return RecipeCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeViewSerializer(
            instance=serializer.instance,
            context={'request': self.request},
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    @action(
        methods=('post', 'delete'),
        detail=True,
        url_path='favorite',
        permission_classes=(IsAuthenticated, ),
    )
    def set_favorite(self, request, pk=id):
        user = request.user
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite = Favorites.objects.create(user=user, recipe=recipe)
            serializer = FavoritesSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite = get_object_or_404(Favorites, user=user, recipe__id=pk)
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
            in_shopping_cart = ShoppingCart.objects.create(
                user=user,
                recipe=recipe
            )
            serializer = ShoppingCartSerializer(in_shopping_cart)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        in_shopping_cart = get_object_or_404(
            ShoppingCart,
            user=user,
            recipe__id=pk
        )
        in_shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        shopping_cart = IngredientInRecipe.objects.filter(
            recipe__shopping_cart_recipe__user=request.user
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
            'attachment; filename="shopping-list.pdf"'
        )
        return response

    # def create_pdf(ingredients):
    #     app_path = path.realpath(path.dirname(__file__))
    #     font_path = path.join(app_path, 'font/PFAgoraSlabPro Bold.ttf')
    #     pdfmetrics.registerFont(TTFont('PFAgoraSlabPro Bold', font_path))
    #     response = HttpResponse(content_type='application/pdf')
    #     response['Content-Disposition'] = ('attachment;'
    #                                        'filename="shopping_list.pdf"')
    #     page = canvas.Canvas(response)
    #     page.setFont('PFAgoraSlabPro Bold', size=25)
    #     page.drawString(200, 800, 'Список покупок.')
    #     page.setFont('PFAgoraSlabPro Bold', size=18)
    #     height = 750
    #     for ingredient_num, (ingredient) in enumerate(ingredients, 1):
    #         page.drawString(
    #             48, height, (f'№ {ingredient_num}. {ingredient["ingredient__name"]} - {ingredient["amount_sum"]}'
    #                          f'{ingredient["ingredient__measurement_unit"]}'))
    #         height -= 25
    #     page.showPage()
    #     page.save()
    #     return response
    #
    # @action(detail=False, methods=['GET'],
    #         permission_classes=[IsAuthenticated])
    # def download_shopping_cart(self, request):
    #     ingredients = IngredientInRecipe.objects.filter(
    #         recipe__shopping_cart_recipe__user=request.user).values(
    #             'ingredient__name', 'ingredient__measurement_unit').annotate(
    #                 amount_sum=Sum('amount')).order_by('ingredient__name')
    #
    #     return self.create_pdf(ingredients=ingredients)
