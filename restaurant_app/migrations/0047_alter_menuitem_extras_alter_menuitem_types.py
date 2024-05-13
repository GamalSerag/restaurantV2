# Generated by Django 5.0.1 on 2024-05-08 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0046_alter_menuitem_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='extras',
            field=models.ManyToManyField(blank=True, null=True, to='restaurant_app.menuitemextra'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='types',
            field=models.ManyToManyField(blank=True, null=True, to='restaurant_app.menuitemtype'),
        ),
    ]
