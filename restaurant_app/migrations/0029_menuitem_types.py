# Generated by Django 5.0.2 on 2024-02-24 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0028_menuitemtype_alter_menuitem_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='types',
            field=models.ManyToManyField(blank=True, to='restaurant_app.menuitemtype'),
        ),
    ]
