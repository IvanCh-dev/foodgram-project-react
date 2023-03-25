from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import Subscription
from api.serializers import RecipeSubscSerializer

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания объеката кастомной модели User."""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'password')


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


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля кастомной модели User."""
    model = User
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


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
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSubscSerializer(
            recipes, many=True, context={'request': request})
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
