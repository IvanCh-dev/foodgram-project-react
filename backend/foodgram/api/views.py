from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.decorators import action
from recipes.models import (
    Ingredient, Tag, Recipe, Favorite, Cart, IngredientAmount)
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    '''ViewSet для модели тегов.'''
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    '''ViewSet для модели ингредиентов.'''
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    '''ViewSet для модели рецептов.'''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, context={}, *args, **kwargs):
        context['request'] = self.request
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(recipe=recipe, user=user).exists():
                return Response({
                    'errors': 'Ошибка, данный рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)

            Favorite.objects.create(recipe=recipe, user=user)
            serializer = RecipeSerializer(
                Recipe.objects.get(id=recipe.id), context=context)
            return Response(serializer.data, status.HTTP_201_CREATED)

        get_object_or_404(Favorite, recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, context={}, *args, **kwargs):
        context['request'] = self.request
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user

        if request.method == 'POST':
            if Cart.objects.filter(recipe=recipe, user=user).exists():
                return Response({
                    'errors': 'Ошибка, данный рецепт уже в списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)

            Cart.objects.create(recipe=recipe, user=user)
            serializer = RecipeSerializer(
                Recipe.objects.get(id=recipe.id), context=context)
            return Response(serializer.data, status.HTTP_201_CREATED)

        get_object_or_404(Cart, recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, context={}, *args, **kwargs):
        context['request'] = self.request
        user = request.user
        queryset = IngredientAmount.objects.filter(
            recipe__carts__user=user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                total_amount=Sum('amount'))
        shopping_list = render_to_string(
            'shopping_list.txt', {'shopping_list': queryset})
        shopping_list = shopping_list.strip().replace('\n\n', '\n')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
