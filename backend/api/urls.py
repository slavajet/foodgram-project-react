from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (CustomUserViewSet, TagViewSet, IngredientViewSet,
                    RecipeViewSet)

router = DefaultRouter()

router.register(r'users', CustomUserViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'recipes', RecipeViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path('auth/', include('djoser.urls.authtoken')),
]
