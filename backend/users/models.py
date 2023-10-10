from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Модель пользователей, расширяющая стандартную модель AbstractUser.
    """
    email = models.EmailField(unique=True, max_length=254)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    """
    Модель подписок между пользователями.
    """
    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик',
    )
    subscribing = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Пользователь, на которого подписались',
    )

    class Meta:
        ordering = ['-id']
        unique_together = ('subscriber', 'subscribing')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber} подписан на {self.subscribing}'
