import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import \
    UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag, Favorites, ShoppingList

from .validation import (validate_cooking_time, validate_ingredients,
                         validate_tags)

User = get_user_model()

COMMON_USER_FIELDS = ('id', 'email', 'username', 'first_name', 'last_name',)
COMMON_RECIPE_FIELDS = ('id', 'tags', 'author', 'ingredients',
                        'name', 'image', 'text', 'cooking_time')


class CustomUserCreateSerializer(DjoserUserCreateSerializer):
    """
    Сериализатор для создания пользователей.
    """
    class Meta:
        model = User
        fields = COMMON_USER_FIELDS + ('password',)


class CustomUserSerializer(DjoserUserSerializer):
    """
    Сериализатор пользователей.
    Добавляет поле "is_subscribed" для определения, подписан ли текущий
    пользователь на данного пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = COMMON_USER_FIELDS + ('is_subscribed',)

    def get_is_subscribed(self, user):
        """
        Метод для определения, подписан ли текущий пользователь
        на данного пользователя.
        """
        if user.is_authenticated:
            return user.subscriptions.filter(subscriber=user).exists()
        return None


class UserRecipeSerializer(CustomUserSerializer):
    """
    Сериализатор для получения информации о пользователе с дополнительными
    данными о подписках и рецептах.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = COMMON_USER_FIELDS + ('is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('id',)

    def get_recipes(self, obj) -> list:
        """
        Получает список рецептов пользователя.
        recipes_limit: Если параметр указан в запросе, то ограничивает кол-во
        рецептов в ответе.
        """
        recipes_limit = self.context['request'].query_params.get('recipes_limit')
        recipes = obj.recipes.all()

        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        return list(RecipeShortSerializer(recipes, many=True).data)

    def get_recipes_count(self, obj) -> int:
        """
        Получает количество рецептов пользователя.
        """
        return Recipe.objects.filter(author=obj).count()

    def validate(self, data):
        """
        Проверяет валидность данных перед их сериализацией,
        И не подписывается ли пользователь на самого себя.
        """
        id = data.get('id')
        request = self.context['request']
        if id == request.user.id:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        return data


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тегов.
    """
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class Base64ImageField(serializers.ImageField):
    """
    Пользовательское поле для обработки изображений в формате base64.
    """
    def to_internal_value(self, data):
        """
        Метод для преобразования данных в формате base64 в объекты ContentFile.
        """
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')
        return super().to_internal_value(data)


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для получения краткой информации о рецептах.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов в рецептах.
    Используется для предоставления информации об ингредиентах, используемых в рецептах.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class AmountSerializer(serializers.ModelSerializer):
    """
    Сериализатор для количества ингредиентов в рецептах.
    Используется для предоставления информации о количестве ингредиентов, используемых в рецептах.
    """
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.
    Используется для создания и обновления рецептов, включая валидацию данных,
    связанных с рецептом, таких как теги, время приготовления и ингредиенты.
    """
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = COMMON_RECIPE_FIELDS

    def validate(self, data):
        """
        Проверяет валидность данных при создании или обновлении рецепта.
        """
        tags = data.get('tags', [])
        cooking_time = data.get('cooking_time')
        ingredients = data.get('ingredients', [])

        validate_tags(tags)
        validate_cooking_time(cooking_time)
        validate_ingredients(ingredients)

        return data

    def add_ingredients(self, ingredients, recipe: Recipe) -> None:
        """
        Добавление ингредиентов к рецепту.
        """
        ingredients_to_create = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient["id"],
                amount=ingredient["amount"],
            )
            for ingredient in ingredients]

        RecipeIngredient.objects.bulk_create(ingredients_to_create)

    def create(self, validated_data) -> Recipe:
        """
        Создание нового рецепта.
        """
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        """
        Представление рецепта для чтения.
        """
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data

    def update(self, instance: Recipe, validated_data) -> Recipe:
        """
        Обновление существующего рецепта.
        """
        instance.tags.clear()
        instance.ingredients.clear()
        instance.name = validated_data['name']
        instance.text = validated_data['text']
        instance.cooking_time = validated_data['cooking_time']
        instance.image = validated_data['image']
        instance.save()
        tags = validated_data.get('tags', [])
        instance.tags.set(tags)
        ingredients = validated_data.get('ingredients', [])
        self.add_ingredients(ingredients, instance)

        return instance


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения рецептов.
    Используется для представления информации о рецепте в ответах API.
    Включает информацию о рецепте, его ингредиентах, тегах, авторе
    и статусах "избранного" и "в корзине покупок".
    """
    ingredients = AmountSerializer(many=True, source='recipe_ingredients')
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = COMMON_RECIPE_FIELDS + ('is_favorited', 'is_in_shopping_cart',)

    def get_is_favorited(self, obj):
        """
        Определение, добавлен ли рецепт в избранное.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorites.objects.filter(recipe=obj.id, user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Определение, добавлен ли рецепт в корзину покупок.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingList.objects.filter(recipe=obj.id, user=user).exists()
        return False
