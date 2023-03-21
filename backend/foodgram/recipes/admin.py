from django.contrib import admin

from .models import (
    Cart, Favorite, Ingredient, IngredientAmount, Recipe, RecipeTag, Tag)


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    min_num = 1


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites')
    inlines = (
        TagInline,
        IngredientInline,
    )
    list_filter = ('author', 'name', 'tags')

    def favorites(self, obj):
        return obj.favorites.count()

    favorites.short_description = 'В избранном'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTag)
admin.site.register(IngredientAmount)
admin.site.register(Favorite)
admin.site.register(Cart)
