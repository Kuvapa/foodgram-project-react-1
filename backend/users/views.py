from api.pagination import CustomPagination
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.serializers import SubscriptionSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination
    lookup_field = 'id'
    search_fields = ('username',)

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
        queryset = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = SubscriptionSerializer(
            queryset,
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
        author = get_object_or_404(User, id=id)
        user = self.request.user
        if request.method == 'POST':
            subscription = get_object_or_404(
                Subscription,
                author=get_object_or_404(User, id=id),
                user=request.user
            )
            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionSerializer(
                subscription,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                author=author
            )
            if not subscription.exists():
                return Response(
                    {'errors': 'Вы не подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_204_NO_CONTENT)
