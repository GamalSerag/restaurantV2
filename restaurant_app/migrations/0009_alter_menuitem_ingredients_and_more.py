# Generated by Django 5.0.1 on 2024-01-28 14:44

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0008_alter_menuitem_ingredients_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='ingredients',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100, null=True), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='sizes_and_prices',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.JSONField(), default=list, size=None),
        ),
    ]
