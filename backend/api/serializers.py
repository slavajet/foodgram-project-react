from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .validation import validate_tags, validate_cooking_time, validate_ingredients
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from users.models import Subscription

import base64
from django.core.files.base import ContentFile

User = get_user_model()


class CustomUserCreateSerializer(DjoserUserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')


class CustomUserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    id = serializers.IntegerField(default=serializers.CurrentUserDefault())

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, user):
        if user.is_authenticated:
            return user.subscriptions.filter(subscriber=user).exists()
        return None


class UserSubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    id = serializers.IntegerField(default=serializers.CurrentUserDefault())

    class Meta(CustomUserSerializer.Meta):
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        id = data.get('id')
        request = self.context['request']
        if id == request.user.id:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        return data

    def get_recipes(self, obj):
        user = obj.subscriber
        recipes = user.recipes.all()[:3]
        return list(RecipeShortSerializer(recipes, many=True).data)

    def get_recipes_count(self, user) -> int:
        return Recipe.objects.filter(author=user).count()


class SubscriptionListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='subscriber.id')
    email = serializers.CharField(source='subscriber.email')
    username = serializers.CharField(source='subscriber.username')
    first_name = serializers.CharField(source='subscriber.first_name')
    last_name = serializers.CharField(source='subscriber.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        user = obj.subscriber
        recipes = user.recipes.all()[:3]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        user = obj.subscriber
        return Recipe.objects.filter(author=user).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')
        return super().to_internal_value(data)


class RecipeShortSerializer(serializers.ModelSerializer):
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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate(self, data):
        tags = data.get('tags', [])
        cooking_time = data.get('cooking_time')
        ingredients = data.get('ingredients', [])

        validate_tags(tags)
        validate_cooking_time(cooking_time)
        validate_ingredients(ingredients)

        return data

    def add_ingredients(self, ingredients, recipe: Recipe) -> None:
        ingredients_to_create = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient["id"],
                amount=ingredient["amount"],
            )
            for ingredient in ingredients]

        RecipeIngredient.objects.bulk_create(ingredients_to_create)

    def create(self, validated_data) -> Recipe:
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data

    def update(self, instance: Recipe, validated_data) -> Recipe:
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
    ingredients = AmountSerializer(many=True, source='recipe_ingredients')
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by_users.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shoppinglist_set.filter(user=request.user).exists()
        return False
