from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class CustomUserCreateSerializer(DjoserUserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')


class CustomUserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, user):
        if user.is_authenticated:
            return user.subscriptions.filter(subscriber=user).exists()
        return None
