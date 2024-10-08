# Generated by Django 5.0.2 on 2024-02-12 11:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers_app', '0003_remove_offer_menu_item'),
        ('restaurant_app', '0014_remove_restaurant_order_modes_delete_ordermode_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='offer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='offers_app.offer'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='offer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='offers_app.offer'),
        ),
    ]
