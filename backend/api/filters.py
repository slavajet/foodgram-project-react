from django.contrib.auth import get_user_model

import django_filters

from recipes.models import Ingredient, Recipe

User = get_user_model()


class IngredientFilter(django_filters.FilterSet):
    """
    Позволяет произвести фильтрацию ингредиентов по названию.
    """
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    """
    Фильтры рецпептов, позволяют фильтровать рецепты по автору, тегам,
    а так же фильтровать избранные рецепты и те которые находятся в корзине.
    """
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = django_filters.NumberFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def get_is_favorited(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по избранному.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorited_by_users__user=self.request.user
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Метод для фильтрации рецептов по добавленным в корзину.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopping_list__user=self.request.user
            )
        return queryset
