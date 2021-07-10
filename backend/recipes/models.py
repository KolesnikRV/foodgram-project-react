from colorfield.fields import ColorField  # noqa
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        help_text='Введите название тега',
        max_length=50,

    )
    color = ColorField(
        verbose_name='Цвет',
        help_text='Введите цвет тега',
        default='#FF0000'
    )
    slug = models.CharField(
        verbose_name='Название слаг тега',
        help_text='Введите название слаг тега',
        max_length=50,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)


class Ingredient(models.Model):
    class MeasurementChoice(models.TextChoices):
        KILOGRAMM = 'кг', 'кг'
        GRAMM = 'г', 'г'

    name = models.CharField(
        verbose_name='Ингреиент',
        help_text='Введите название ингредиента',
        max_length=70,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица изменения',
        help_text='Выберите единицу измерения',
        choices=MeasurementChoice.choices,
        default=MeasurementChoice.GRAMM,
        max_length=2,

    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Укажите автора рецепта',
        on_delete=models.SET('Пользователь удалён'),
    )
    name = models.CharField(
        verbose_name='Название',
        help_text='Введите название рецепта',
        max_length=100,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Выберите изображение',
    )
    text = models.CharField(
        verbose_name='Текстовое описание',
        help_text='Опишите рецепт',
        max_length=1000,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        help_text='Укажите ингредиенты и их количество',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Выберите один или несколько тегов',
    )
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления(минуты)',
        help_text='Укажите время приготовления в минутах',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)


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
    )

    def __str__(self):
        return f'{self.ingredient}, {self.amount}'

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Рецепт-ингредиент'
        verbose_name_plural = 'Рецепты-ингредиенты'
        ordering = ('recepie__name',)


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
        return f'{self.author} подписан на {self.user}'

    class Meta:
        unique_together = ('author', 'user')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


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
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.recipe.name} в избранном у пользователя {self.user}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('recipe__name',)


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
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.recipe.name} в списке покупок у пользователя {self.user}'

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        ordering = ('recipe__name',)
