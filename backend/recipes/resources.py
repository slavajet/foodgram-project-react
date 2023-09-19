from import_export import resources
from .models import Ingredient

class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient
        exclude = ('id',)
        import_id_fields  = ('name', 'measurement_unit')
