from djoser.views import UserViewSet as DjoserUserViewSet
from .permissions import AllowAllOrIsAuthenticated
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from .serializers import (CustomUserSerializer, TagSerializer,
                          IngredientSerializer, RecipeSerializer)
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import IngredientFilter
from rest_framework.response import Response
from rest_framework import status


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
    search_fields = ['name']


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer) -> None:
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs) -> Response:
        data = request.data.copy()
        data['author'] = request.user.id
        tags_data = data.pop('tags', [])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        recipe = serializer.instance
        recipe.tags.set(tags_data)
        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data
        response_data['id'] = serializer.instance.id
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
