from rest_framework import serializers


def validate_tags(tags) -> None:
    """
    Функция валидации тегов для рецепта.
    """
    if not tags:
        raise serializers.ValidationError('Теги не могут быть пустыми.')
    tag_ids = set()
    for tag in tags:
        if tag.id in tag_ids:
            raise serializers.ValidationError(
                'Нельзя использовать одинаковые теги.'
            )
        tag_ids.add(tag.id)


def validate_ingredients(ingredients) -> None:
    """
    Функция валидации ингредиентов для рецепта.
    """
    if not ingredients:
        raise serializers.ValidationError(
            'Нельзя приготовить что либо без ингредиентов.'
        )
    ingredient_ids = set()
    for ingredient_data in ingredients:
        ingredient_id = ingredient_data.get('id')
        if ingredient_id in ingredient_ids:
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        ingredient_ids.add(ingredient_id)
