# Generated by Django 5.0.2 on 2024-02-12 11:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offers_app', '0002_rename_offers_offer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='menu_item',
        ),
    ]
