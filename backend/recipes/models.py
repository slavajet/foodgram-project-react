from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    Модель для тегов.

    Каждый тег представляет собой метку, которую можно прикрепить к рецепту.
    Теги используются для категоризации рецептов и упрощения их поиска.
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        verbose_name='Цвет в HEX'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Уникальный слаг'
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """
    Модель для ингредиентов.

    Ингредиенты представляют собой отдельные компоненты, которые используются
    при приготовлении рецепта. У каждого ингредиента есть название и единица
    измерения, которые могут быть использованы для определения количества
    ингредиентов в рецептах.
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """
    Модель для рецептов.

    Рецепты представляют собой кулинарные рецепты, которые пользователи могут
    создавать и просматривать на сайте. У каждого рецепта есть название,
    описание, время приготовления, изображение, автор, теги и ингредиенты.
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(verbose_name='Время приготовления')
    image = models.ImageField(blank=True, null=True, verbose_name='Изображение')  # noqa: E501
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredient(models.Model):
    """
    Модель для ингредиентов рецепта.

    Каждый объект этой модели представляет собой ингредиент, используемый в
    конкретном рецепте. Модель описывает, какое колличество ингредиента
    необходимо для приготовления рецепта.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(verbose_name='Кол-во ингридиентов')

    def __str__(self) -> str:
        return f"{self.recipe.name} - {self.ingredient.name}"

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class Favorites(models.Model):
    """
    Модель для добавления рецептов в избранное пользователей.

    Модель позволяет пользователям добавлять рецепты в свой список избранного.
    Каждый пользователь может добавить в избранное рецепты, которые он хочет
    сохранить для последующего просмотра.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorited_by_users',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by_users',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return f'{self.user} добавил в избранное рецепт "{self.recipe}"'


class ShoppingList(models.Model):
    """
    Модель для списка покупок.

    Эта модель представляет собой список покупок, связанный с конкретным
    пользователем и рецептом. Пользователи могут добавлять рецепты в свой
    список покупок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self) -> str:
        return f'{self.user} добавил в список покупок рецепт: {self.recipe.name}'  # noqa: E501
