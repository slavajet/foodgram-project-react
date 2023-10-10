from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                     ShoppingList, Tag)
from .resources import IngredientResource, TagResource

MIN_NUM = 1


class RecipeIngredientInline(admin.TabularInline):
    """
    Inline модель для ингредиентов рецепта.
    Позволяет редактировать и добавлять ингредиенты непосредственно на странице
    редактирования рецепта в административной панели.
    Attributes:
        model: Модель, представляющая связь между рецептом и ингредиентом.
        min_num : Минимальное количество ингредиентов, которое должно быть
        связано с рецептом.
    """
    model = RecipeIngredient
    min_num = MIN_NUM


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_class = TagResource
    list_display = ('name', 'color', 'slug')
    list_filter = ('name', 'color')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'cooking_time', 'author',
                    'pub_date', 'total_favorites')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author__username')
    date_hierarchy = 'pub_date'
    inlines = (RecipeIngredientInline,)

    def total_favorites(self, obj):
        """Вычисляет общее кол-во добавления в избранное для каждого рецепта"""
        return obj.favorited_by_users.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__title')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
