from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from .filters import purchase_recipe_imit_filter
from .models import (Favorite, Ingredient, Purchase, Recipe, RecipeIngredient,
                     Tag, User)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = serializers.ALL_FIELDS


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = serializers.ALL_FIELDS


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class ListRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    amount = serializers.IntegerField()
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = ListRecipeIngredientSerializer(source='recipeingredient_set',
                                                 many=True)
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField('recipe_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'recipe_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def recipe_is_favorited(self, obj):
        recipe = get_object_or_404(Recipe, id=obj.id)
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=recipe, user=user).exists()

    def recipe_is_in_shopping_cart(self, obj):
        recipe = get_object_or_404(Recipe, id=obj.id)
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Purchase.objects.filter(recipe=recipe, user=user).exists()


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = RecipeIngredientSerializer(source='recipeingredient_set',
                                             many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)

    class Meta:
        model = Recipe
        exclude = ('id', 'author')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        author = self.context.get('request').user
        recipe = Recipe(author=author, **validated_data)

        recipe_ingredient_list = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            if amount < 1:
                raise serializers.ValidationError(
                    'Убедитесь, что это значение больше либо равно 1.'
                )

            ingredient_instance = get_object_or_404(Ingredient,
                                                    id=ingredient.get('id'))
            recipe_ingredient_list.append(RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_instance,
                amount=amount
            ))

        recipe.save()
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(recipe_ingredient_list)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')

        recipe_ingredient_list = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            if amount < 1:
                raise serializers.ValidationError(
                    'Убедитесь, что это значение больше либо равно 1.'
                )
            ingredient_instance = get_object_or_404(Ingredient,
                                                    id=ingredient.get('id'))
            recipe_ingredient_list.append(RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_instance,
                amount=amount
            ))

        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.name = validated_data.get('name')
        instance.image = validated_data.get('image')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()
        instance.tags.set(tags)
        RecipeIngredient.objects.bulk_create(recipe_ingredient_list)

        return instance


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField('recipes_limit')
    recipes_count = serializers.SerializerMethodField('count_recipes')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def count_recipes(self, user):
        return user.recipes.count()

    def recipes_limit(self, user):
        recipes_query = user.recipes.all()
        recipes_query = purchase_recipe_imit_filter(
            self.context.get('request'),
            recipes_query
        )
        print(recipes_query)
        return RecipeMinifiedSerializer(recipes_query, many=True).data
