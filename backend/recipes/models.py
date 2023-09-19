from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Recipe(models.Model):
    name = models.CharField(max_length=255)
    text = models.TextField()
    cooking_time = models.IntegerField()
    image = models.URLField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', related_name='recipes')
    ingredients = models.ManyToManyField('Ingredient', through='RecipeIngredient', related_name='recipes')

    def __str__(self):
        return self.name
