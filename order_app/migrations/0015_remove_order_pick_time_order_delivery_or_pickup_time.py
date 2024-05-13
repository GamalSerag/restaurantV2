# Generated by Django 5.0.1 on 2024-03-27 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0014_order_order_mode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='pick_time',
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_or_pickup_time',
            field=models.DateTimeField(blank=True, help_text='Specify the time for delivery or pickup based on the order mode.', null=True),
        ),
    ]
