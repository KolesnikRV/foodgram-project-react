from django_filters import rest_framework as filters

from .models import Recipe


class CustomFilter(filters.FilterSet):
    author = filters.filters.CharFilter()
    tags = filters.filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.filters.BooleanFilter(method='recipe_is_favorited')
    is_in_shopping_cart = filters.filters.BooleanFilter(
        method='recipe_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def recipe_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorited__user=user)
        return queryset

    def recipe_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(in_purchase_list__user=user)
        return queryset


def purchase_recipe_imit_filter(request, queryset):
    recipes_limit = request.query_params.get('recipes_limit')
    if recipes_limit:
        return queryset[:int(recipes_limit)]
    return queryset
