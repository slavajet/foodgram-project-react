# Generated by Django 4.2.5 on 2023-09-21 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_shoppinglist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Изображение'),
        ),
    ]
