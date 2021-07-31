from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название тега',
        max_length=200,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет в HEX',
        help_text='Введите цвет тега в HEX',
        unique=True,
        null=True,
    )
    slug = models.CharField(
        verbose_name='Уникальный слаг',
        help_text='Введите уникальный слаг',
        max_length=200,
        unique=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Недопустимые символы.'
            )
        ]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингреиент',
        help_text='Введите название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица изменения',
        help_text='Выберите единицу измерения',
        max_length=200,
    )

    def __str__(self):
        return f'{self.name}  -  ({self.measurement_unit})'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        help_text='Укажите автора рецепта',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название рецепта',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Выберите изображение',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Опишите рецепт',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        help_text='Укажите ингредиенты и их количество',
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Выберите один или несколько тегов',
    )
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления(минуты)',
        help_text='Укажите время приготовления в минутах',
        validators=[MinValueValidator(1, 'Значение не может быть меньше 1')],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.SmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1, 'Значение не может быть меньше 1')],

    )

    def __str__(self):
        return f'{self.ingredient}, {self.amount}'

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Рецепт-ингредиент'
        verbose_name_plural = 'Рецепты-ингредиенты'
        ordering = ('recipe__name',)


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Подписан',
        related_name='following',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

    class Meta:
        unique_together = ('author', 'user')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('author', 'user')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorite_recipe',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favorited',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.recipe.name} в избранном у пользователя {self.user}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('recipe__name',)
        unique_together = ('recipe', 'user')


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='purchase_list',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='in_purchase_list',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return (f'{self.recipe.name}'
                'в списке покупок у пользователя {self.user}')

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ('recipe__name',)

    @classmethod
    def get_purchase_list(cls, purchase_queryset):
        purchase_list = {}
        for purchase in purchase_queryset:
            ingredients = RecipeIngredient.objects.filter(
                recipe=purchase.recipe
            ).prefetch_related('ingredient')

            for ingredient in ingredients:
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount
                if ingredient.ingredient.name in purchase_list:
                    purchase_list[name]['amount'] += amount
                else:
                    purchase_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }

        return purchase_list
