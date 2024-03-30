from django.contrib import admin

from recipes.models import (
    Recipes,
    Tags,
    Ingredients,
    IngredientsRecipes,
    Favorites,
    Carts
)


class RecipesAdmin(admin.ModelAdmin):
    """Регистрация модели `Recipe` для админки."""
    list_display = (
        'name',
        'author',
        'image',
        'text',
        'cooking_time',
        'favorite_count'
    )
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags', 'ingredients')

    def favorite_count(self, obj):
        return Favorites.objects.filter(recipe_id=obj.id).count()


class IngredientsAdmin(admin.ModelAdmin):
    """Регистрация модели `Tag` для админки."""
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


class TagsAdmin(admin.ModelAdmin):
    """Регистрация модели `Tag` для админки."""
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )


admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(IngredientsRecipes)
admin.site.register(Favorites)
admin.site.register(Carts)
