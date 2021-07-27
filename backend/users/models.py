from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
        max_length=254,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]',
                message='Недопустимые символы.'
            )
        ]
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        unique=True,
        max_length=150,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
