# Generated by Django 5.0.1 on 2024-01-27 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0004_alter_ordermode_name_alter_restaurant_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermode',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='state',
            field=models.BooleanField(default='True'),
        ),
    ]
