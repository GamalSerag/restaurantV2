# Generated by Django 5.0.2 on 2024-02-25 09:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0029_menuitem_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitemtypeitem',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='restaurant_app.menuitemtype'),
        ),
    ]
