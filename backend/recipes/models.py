from django.db import models
from django.contrib.auth import get_user_model

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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

class Ingredient(models.Model):
    """
    Модель для ингредиентов.

    Ингредиенты представляют собой отдельные компоненты, которые используются
    при приготовлении рецепта. У каждого ингредиента есть название и единица измерения,
    которые могут быть использованы для определения количества ингредиентов в рецептах.
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(max_length=200, verbose_name='Единица измерения')

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """
    Модель для рецептов.

    Рецепты представляют собой кулинарные рецепты, которые пользователи могут создавать
    и просматривать на сайте. У каждого рецепта есть название, описание, время приготовления,
    изображение, автор, теги и ингредиенты.
    """
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(verbose_name='Время приготовления в минутах')
    image = models.URLField(blank=True, null=True, verbose_name='Изображение')
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

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)


class RecipeIngredient(models.Model):
    """
    Модель для ингредиентов рецепта.

    Каждый объект этой модели представляет собой ингредиент, используемый в конкретном рецепте.
    Модель описывает, какое колличество ингредиента необходимо для приготовления рецепта.
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
    amount = models.PositiveIntegerField(verbose_name='Колличество ингридиентов')

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredient.name}"

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
