# Generated by Django 5.0.1 on 2024-04-14 09:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0023_alter_order_options_alter_deliverydetails_area_and_more'),
        ('review_app', '0005_remove_deliveryrating_restaurant_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='totalrating',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='order_app.order'),
        ),
    ]
