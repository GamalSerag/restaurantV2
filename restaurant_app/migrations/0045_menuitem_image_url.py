# Generated by Django 5.0.1 on 2024-05-08 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0044_alter_restaurantcategory_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='image_url',
            field=models.URLField(null=True),
        ),
    ]
