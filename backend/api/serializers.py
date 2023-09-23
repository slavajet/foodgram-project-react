from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient

import base64
from django.core.files.base import ContentFile

User = get_user_model()


class CustomUserCreateSerializer(DjoserUserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')


class CustomUserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, user):
        if user.is_authenticated:
            return user.subscriptions.filter(subscriber=user).exists()
        return None


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class Base64ImageField(serializers.ImageField):
    """
    Custom serializer field for handling Base64-encoded images.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')
        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(required=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
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

