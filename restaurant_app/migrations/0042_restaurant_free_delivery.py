# Generated by Django 5.0.1 on 2024-04-16 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0041_remove_restaurant_free_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='free_delivery',
            field=models.BooleanField(default='False'),
        ),
    ]
