from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator


User = get_user_model()


class Ingredient(models.Model):
    '''Модель ингредиентов.'''
    name = models.CharField(max_length=64, verbose_name='Название')
    measurement_unit = models.CharField(max_length=16,
                                        verbose_name='Единица измерения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    '''Модель тегов.'''
    name = models.CharField(
        unique=True, max_length=64, verbose_name='Название')
    color = models.CharField(unique=True, max_length=16, verbose_name='Цвет')
    slug = models.SlugField(unique=True,
                            verbose_name='Адрес')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    '''Модель рецептов.'''
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор рецепта')
    name = models.CharField(max_length=64, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    tags = models.ManyToManyField(Tag, through='RecipeTag',
                                  through_fields=('recipe', 'tag'),
                                  verbose_name='Список id тегов'
                                  )
    ingredients = models.ManyToManyField(
                Ingredient, through='IngredientAmount',
                through_fields=('recipe', 'ingredient'),
                verbose_name='Список ингредиентов'
                )
    cooking_time = models.PositiveSmallIntegerField(
                 verbose_name='Время приготовления (в минутах)',
                 validators=[MinValueValidator(1), ])
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
    image = models.ImageField(
        upload_to='recipes/', verbose_name='Картинка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class RecipeTag(models.Model):
    '''Вспомогательная модель ГецептТег.'''
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tagrecipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tagrecipes',
    )

    def __str__(self):
        return f'Рецепт {self.recipe}, тег {self.tag}'

    class Meta:
        verbose_name = 'РецептТег'
        verbose_name_plural = 'РецептТег'


class IngredientAmount(models.Model):
    '''Вспомогательная модель ИнгредиентКоличество.'''
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientamount',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientamount',
    )
    amount = models.IntegerField(
                 verbose_name='Количество в рецепте')

    def __str__(self):
        return f'Рецепт {self.recipe}, ингредиент {self.ingredient}'

    class Meta:
        verbose_name = 'ИнгредиентКоличество'
        verbose_name_plural = 'ИнгредиентКоличество'


class Favorite(models.Model):
    '''Модель избранное.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='В избранном у')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'Рецепт {self.recipe}, в избранном у {self.user}'


class Cart(models.Model):
    '''Модель корзины покупок.'''
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепт списке покупок')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='carts',
        verbose_name='Владелец списка покупок')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'Рецепт {self.recipe}, в списке покупок у {self.user}'
