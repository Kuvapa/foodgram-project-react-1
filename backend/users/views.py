from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.serializers import SubscriptionSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User


class CustomUserViewSet(UserViewSet):
    pagination_class = PageNumberPagination

    @action(
        methods=('get',),
        url_path='me',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_self_page(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('get',),
        url_path='subscriptions',
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post', 'delete'),
        url_path='subscribe',
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        if request.method == 'POST':
            user = request.user
            author = get_object_or_404(User, id=id)

            data = {
                'user': user.id,
                'author': author.id,
                'email': author.email,
            }
            serializer = SubscriptionSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            user = request.user
            author = get_object_or_404(User, id=id)
            subscribe = get_object_or_404(
                Subscription, user=user, author=author
            )
            subscribe.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
