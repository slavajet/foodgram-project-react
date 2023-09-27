# validation.py
from rest_framework import serializers


def validate_tags(tags):
    if not tags:
        raise serializers.ValidationError("Tags list cannot be empty.")
    tag_ids = set()
    for tag in tags:
        if tag.id in tag_ids:
            raise serializers.ValidationError("Duplicate tags are not allowed.")
        tag_ids.add(tag.id)


def validate_cooking_time(cooking_time):
    if cooking_time is not None and cooking_time < 1:
        raise serializers.ValidationError("Cooking time must be 1 or greater.")


def validate_ingredients(ingredients):
    if not ingredients:
        raise serializers.ValidationError("Ingredients list cannot be empty.")
    ingredient_ids = set()
    for ingredient_data in ingredients:
        ingredient_id = ingredient_data.get('id')
        if ingredient_id in ingredient_ids:
            raise serializers.ValidationError("Duplicate ingredients are not allowed.")
        ingredient_ids.add(ingredient_id)

        amount = ingredient_data.get('amount')
        if amount is None or amount < 1:
            raise serializers.ValidationError("Ingredient amount must be 1 or greater.")
