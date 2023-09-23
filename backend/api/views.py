from djoser.views import UserViewSet as DjoserUserViewSet
from .permissions import AllowAllOrIsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.serializers import CustomUserSerializer


class CustomUserViewSet(DjoserUserViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAllOrIsAuthenticated]
    
