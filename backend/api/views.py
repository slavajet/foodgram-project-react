from djoser.views import UserViewSet as DjoserUserViewSet
from .permissions import AllowAllOrIsAuthenticated
from recipes.models import Tag, Ingredient
from .serializers import (CustomUserSerializer, TagSerializer,
                          IngredientSerializer)
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CustomUserViewSet(DjoserUserViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAllOrIsAuthenticated]


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngridientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
