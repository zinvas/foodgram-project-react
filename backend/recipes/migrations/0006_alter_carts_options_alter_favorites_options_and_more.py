# Generated by Django 4.2.11 on 2024-03-30 16:22

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0005_alter_ingredientsrecipes_ingredient_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='carts',
            options={'ordering': ['-id'], 'verbose_name': 'Корзина покупок', 'verbose_name_plural': 'Корзины покупок'},
        ),
        migrations.AlterModelOptions(
            name='favorites',
            options={'ordering': ['-id'], 'verbose_name': 'Избраннный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='ingredients',
            options={'ordering': ['-id'], 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientsrecipes',
            options={'ordering': ['-id'], 'verbose_name': 'Ингредиенты в рецепте'},
        ),
        migrations.AlterModelOptions(
            name='recipes',
            options={'ordering': ['-id'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='tags',
            options={'ordering': ['-id'], 'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterField(
            model_name='carts',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='recipes.recipes', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='carts',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='recipes.recipes', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='ingredients',
            name='measurement_unit',
            field=models.CharField(max_length=200, verbose_name='Ед. измерения'),
        ),
        migrations.AlterField(
            model_name='ingredients',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientsrecipes',
            name='amount',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1, message='Must be higher than 1.')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='ingredientsrecipes',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientsrecipes', to='recipes.ingredients', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientsrecipes',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientsrecipes', to='recipes.recipes', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='recipes',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='recipes',
            name='cooking_time',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Must be higher than 1.')], verbose_name='Время готовки'),
        ),
        migrations.AlterField(
            model_name='recipes',
            name='image',
            field=models.ImageField(default=None, upload_to='recipes/images/', verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='recipes',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.IngredientsRecipes', to='recipes.ingredients', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipes',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='recipes',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='recipes',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.tags', verbose_name='Тэги'),
        ),
        migrations.AlterField(
            model_name='recipes',
            name='text',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='tags',
            name='color',
            field=models.CharField(max_length=7, unique=True, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='tags',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='tags',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, verbose_name='Слаг'),
        ),
    ]
