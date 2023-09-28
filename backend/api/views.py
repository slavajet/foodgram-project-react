from djoser.views import UserViewSet as DjoserUserViewSet
from .permissions import AllowAllOrIsAuthenticated, IsRecipeAuthorOrReadOnly
from recipes.models import Tag, Ingredient, Recipe
from users.models import Subscription
from .pagination import Paginator
from .serializers import (CustomUserSerializer, TagSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, UserSubscribeSerializer,
                          SubscriptionListSerializer)
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter, RecipeFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action


class CustomUserViewSet(DjoserUserViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAllOrIsAuthenticated, IsAuthenticated]
    pagination_class = Paginator

    @action(detail=True, methods=['post'])
    def subscribe(self, request, id=None) -> Response:
        user_to_subscribe = self.get_object()
        if request.user == user_to_subscribe:
            return Response(
                {'detail': 'Вы не можете подписаться на себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            subscribing=user_to_subscribe
        )

        if created:
            serializer = UserSubscribeSerializer(
                user_to_subscribe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['delete'])
    def unsubscribe(self, request, id=None) -> Response:
        user_to_unsubscribe = self.get_object()

        Subscription.objects.filter(
            subscriber=request.user,
            subscribing=user_to_unsubscribe
        ).delete()
        return Response(
            {'detail': 'Отписка удалась.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(subscriber=user)
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = IngredientFilter
    search_fields = ['author', 'tags']


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsRecipeAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RecipeFilter
    search_fields = ['name']
    pagination_class = Paginator

    def get_serializer_class(self):
        if self.action == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
