from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='recipes',
        verbose_name='Автор',
        null=True
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/',
        default=None
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        'Ingredients',
        through='IngredientsRecipes',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        'Tags',
        related_name='recipes',
        verbose_name='Тэги'
    )
    cooking_time = models.PositiveIntegerField(
        'Время готовки',
        validators=[MinValueValidator(1, message='Must be higher than 1.')]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return f'{self.name}'


class Tags(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет', max_length=7, unique=True)
    slug = models.SlugField('Слаг', max_length=200, unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return f'{self.name}'


class Ingredients(models.Model):
    name = models.CharField('Ингредиент', max_length=200)
    measurement_unit = models.CharField('Ед. измерения', max_length=200)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.name}'


class IngredientsRecipes(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredientsrecipes',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='ingredientsrecipes',
        verbose_name='Рецепт'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        default=0,
        validators=[MinValueValidator(1, message='Must be higher than 1.')]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    def __str__(self) -> str:
        return f'{self.user} {self.recipe}'

    class Meta:
        ordering = ['-id']
        models.constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_for_user'
            )
        ]
        verbose_name = 'Избраннный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class Carts(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепт'
    )

    def __str__(self) -> str:
        return f'{self.user} {self.recipe}'

    class Meta:
        ordering = ['-id']
        models.constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='recipe_for_user'
            )
        ]
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
