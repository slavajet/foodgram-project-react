from import_export import resources

from .models import Ingredient, Tag


class IngredientResource(resources.ModelResource):
    """
    Ресурс для импорта и экспорта модели Ingredient.
    """
    class Meta:
        model = Ingredient
        exclude = ('id',)
        import_id_fields = ('name', 'measurement_unit')


class TagResource(resources.ModelResource):
    """
    Ресурс для импорта и экспорта модели Tag.
    """
    class Meta:
        model = Tag
        exclude = ('id',)
        import_id_fields = ('name', 'color', 'slug')
