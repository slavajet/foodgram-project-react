from djoser.views import UserViewSet as DjoserUserViewSet
from .permissions import AllowAllOrIsAuthenticated
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from .serializers import (CustomUserSerializer, TagSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer)
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter, RecipeFilter
from rest_framework.response import Response
from rest_framework import status
import logging


class CustomUserViewSet(DjoserUserViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAllOrIsAuthenticated]


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
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RecipeFilter
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

