# Generated by Django 5.0.2 on 2024-03-04 12:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('delivery_app', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='delivery',
            old_name='timestamps',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='deliveryman',
            old_name='timestamps',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='deliveryroute',
            old_name='timestamps',
            new_name='created_at',
        ),
    ]
