from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель User."""
    username = models.CharField(
        db_index=True,
        max_length=150,
        unique=True,
        verbose_name='Логин',
    )
    email = models.EmailField(
        db_index=True,
        unique=True,
        max_length=254,
        verbose_name='Почтовый адрес',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-username']

    def __str__(self):
        """Строковое представление модели."""
        return self.username


class Subscription(models.Model):
    """Модель подписок пользователей друг на друга."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers',
        verbose_name='Автор рецепта')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions',
        verbose_name='Подписчик')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-author']

    def __str__(self):
        """Строковое представление модели."""
        return f'Пользователь {self.user}, подписан на  {self.author}'
