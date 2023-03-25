import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (
    Cart, Favorite, Ingredient, IngredientAmount, Recipe, RecipeTag, Tag)

from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор чтения объеката кастомной модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user_id = obj.id if isinstance(obj, User) else obj.author.id
        request_user = self.context.get('request').user.id
        return Subscription.objects.filter(author=user_id,
                                           user=request_user).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'recipes_count', 'recipes')

    def get_is_subscribed(self, obj):
        user_id = obj.id if isinstance(obj, User) else obj.author.id
        request_user = self.context.get('request').user.id
        return Subscription.objects.filter(author=user_id,
                                           user=request_user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        serializer = RecipeSubscSerializer(
            recipes, many=True, context={'request': request})
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class Base64ImageField(serializers.ImageField):
    """Сериализатор для работы с картинками в Base64."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с чтением ИнгредиентКоличество."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с созданием ИнгредиентКоличество."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredientamount',
    )
    image = Base64ImageField()
    author = CustomUserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'text', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart', 'image')
        read_only_fields = ('id', 'author')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context['request'].method in ['POST', 'PATCH']:
            self.fields['ingredients'] = IngredientAmountCreateSerializer(
                many=True, write_only=True,)
            self.fields['tags'] = serializers.PrimaryKeyRelatedField(
                many=True,
                queryset=Tag.objects.all())

    def get_is_favorited(self, obj):
        recipe = obj.id if isinstance(obj, Recipe) else obj.recipe.id
        request_user = self.context.get('request').user.id
        return Favorite.objects.filter(recipe=recipe,
                                       user=request_user).exists()

    def get_is_in_shopping_cart(self, obj):
        recipe = obj.id if isinstance(obj, Recipe) else obj.recipe.id
        request_user = self.context.get('request').user.id
        return Cart.objects.filter(
            recipe=recipe, user=request_user).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags_data:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        ingredient_amounts = [
            IngredientAmount(
                recipe=recipe, ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        IngredientAmount.objects.bulk_create(ingredient_amounts)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            IngredientAmount.objects.filter(recipe=instance).delete()
            ingredient_amounts = [
                IngredientAmount(
                    recipe=instance, ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount'])
                for ingredient_data in ingredients_data
            ]
            IngredientAmount.objects.bulk_create(ingredient_amounts)
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['ingredients'] = IngredientAmountSerializer(
            instance.ingredientamount.all(), many=True).data
        return ret


class RecipeSubscSerializer(serializers.ModelSerializer):
    """Сокращённый сериализатор для рецептов в подписках и карте."""
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    image = Base64ImageField(source='recipe.image')

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'cooking_time', 'image')
