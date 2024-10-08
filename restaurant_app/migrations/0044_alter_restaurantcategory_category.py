# Generated by Django 5.0.1 on 2024-04-22 12:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0043_restaurant_free_delivery_from'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurantcategory',
            name='category',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restaurant_categories', to='restaurant_app.category'),
        ),
    ]
