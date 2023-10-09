from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Favorites, Ingredient, Recipe, ShoppingList, Tag
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import CustomUser, Subscription

from .filters import IngredientFilter, RecipeFilter
from .pagination import Paginator
from .permissions import AllowAllOrIsAuthenticated, IsRecipeAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeShortSerializer,
                          RecipeWriteSerializer, TagSerializer,
                          UserRecipeSerializer)


class CustomUserViewSet(DjoserUserViewSet):
    """
    Пользовательский ViewSet для пользователей.
    Этот ViewSet обеспечивает работу с пользователями, включая действия,
    такие как подписка и отписка от других пользователей.
    """
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAllOrIsAuthenticated | IsAuthenticated]
    pagination_class = Paginator
    queryset = CustomUser.objects.all()

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs) -> Response | None:
        """
        Метод позволяющий пользователям подписываться и отписываться (на / от)
        авторов рецептов.
        """
        user = request.user
        user_id = self.kwargs.get('id')
        author = get_object_or_404(CustomUser, id=user_id)

        if request.method == 'POST':
            if user.is_anonymous:
                return Response({'detail': 'Сначала нужно авторизоваться.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            if user == author:
                return Response(
                    {'detail': 'Вы не можете подписаться на себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscriptions, created = Subscription.objects.get_or_create(
                subscriber=user,
                subscribing=author
            )

            if created:
                serializer = UserRecipeSerializer(
                    author,
                    context={'request': request}
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            if not Subscription.objects.filter(
                    subscriber=user,
                    subscribing=author
            ).exists():
                return Response(
                    {'detail': 'Подписка не существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Subscription.objects.filter(
                subscriber=user,
                subscribing=author
            ).delete()
            return Response(
                {'detail': 'Отписка удалась.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """
        Получение списка подписок текущего пользователя.
        Это действие позволяет пользователю получить список пользователей,
        на которых он подписан.
        """
        user = request.user
        queryset = CustomUser.objects.filter(subscribers__subscriber=user)
        page = self.paginate_queryset(queryset)
        serializer = UserRecipeSerializer(
            page,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """
    Представление для тегов.
    Этот ViewSet предоставляет доступ к списку тегов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Представление для ингредиентов.
    Этот ViewSet предоставляет доступ к списку ингредиентов и поддерживает
    фильтрацию и поиск.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = IngredientFilter
    search_fields = ['author']


class RecipeViewSet(ModelViewSet):
    """
    Представление для рецептов.
    Этот ViewSet предоставляет доступ к списку рецептов и поддерживает
    фильтрацию, поиск и создание новых рецептов.
    """
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsRecipeAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = Paginator
    ordering_fields = ['-pub_date']

    def get_serializer_class(self) -> type:
        """
        Определение класса сериализатора для представления.
        Возвращает класс сериализатора в зависимости от действия (action) запроса.
        Для GET-запросов используется `RecipeReadSerializer`,
        а для остальных действий - `RecipeWriteSerializer`.
        """
        if self.action == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer) -> None:
        """
        Создание нового рецепта.
        Метод создает новый рецепт, связывает его с текущим авторизованным
        пользователем и сохраняет его.
        """
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance) -> None:
        """
        Удаление рецепта.
        """
        return super().perform_destroy(instance)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk=None) -> Response | None:
        """
        Метод (добавления / удаления) рецепта (в / из) списка покупок.
        """
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            instance = ShoppingList.objects.filter(user=user, recipe=recipe).first()
            if not instance:
                return Response(
                    {'errors': 'Рецепт не был добавлен в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request) -> HttpResponse:
        """
        Метод позволяющий скачать пользователю список всех ингредиентов и их
        колличество из всех рецептов добавленных в список покупок.
        """
        user = request.user

        ingredients = (
            ShoppingList.objects
            .filter(user=user)
            .values(
                'recipe__recipe_ingredients__ingredient__name',
                'recipe__recipe_ingredients__ingredient__measurement_unit'
            )
            .annotate(amount=Sum('recipe__recipe_ingredients__amount'))
        )

        shopping_cart = [f'Список покупок {user}.\n']
        for ingredient in ingredients:
            shopping_cart.append(
                f'{ingredient["recipe__recipe_ingredients__ingredient__name"]} - '
                f'{ingredient["amount"]} '
                f'{ingredient["recipe__recipe_ingredients__ingredient__measurement_unit"]}\n'
            )

        file_name = f'{user.username}_shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated],
        url_path='favorite',
        url_name='favorite',
    )
    def favorite_recipe(self, request, pk=None) -> Response | None:
        """
        Метод (добавления / удаления) рецепта (в / из) избранное.
        """
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if Favorites.objects.filter(user=request.user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorites.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            favorite_recipe = Favorites.objects.filter(user=request.user, recipe=recipe).first()
            if not favorite_recipe:
                return Response(
                    {'errors': 'Рецепт не был добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
