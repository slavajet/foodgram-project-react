from rest_framework import serializers


def validate_tags(tags):
    """
    Функция валидации тегов для рецепта.
    """
    if not tags:
        raise serializers.ValidationError("Теги не могут быть пустыми.")
    tag_ids = set()
    for tag in tags:
        if tag.id in tag_ids:
            raise serializers.ValidationError("Нельзя использовать одинаковые теги.")
        tag_ids.add(tag.id)


def validate_cooking_time(cooking_time):
    """
    Функция валидации времени приготовления рецепта.
    """
    if cooking_time is not None and cooking_time < 1:
        raise serializers.ValidationError("Время приготовления должно быть 1 или больше.")


def validate_ingredients(ingredients):
    """
    Функция валидации ингредиентов для рецепта.
    """
    if not ingredients:
        raise serializers.ValidationError("Нельзя приготовить что либо без ингредиентов.")
    ingredient_ids = set()
    for ingredient_data in ingredients:
        ingredient_id = ingredient_data.get('id')
        if ingredient_id in ingredient_ids:
            raise serializers.ValidationError("Ингредиенты не должны повторяться.")
        ingredient_ids.add(ingredient_id)

        amount = ingredient_data.get('amount')
        if amount is None or amount < 1:
            raise serializers.ValidationError("Игредиентов должно быть 1 или больше.")
