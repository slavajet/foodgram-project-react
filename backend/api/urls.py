from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

router = DefaultRouter()

router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path('auth/', include('djoser.urls.authtoken')),
]
