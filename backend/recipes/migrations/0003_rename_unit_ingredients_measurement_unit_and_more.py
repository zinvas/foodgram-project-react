# Generated by Django 4.2.11 on 2024-03-26 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_ingredients_name_alter_ingredients_unit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredients',
            old_name='unit',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='recipes',
            old_name='time',
            new_name='cooking_time',
        ),
    ]
