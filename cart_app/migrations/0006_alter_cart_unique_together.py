# Generated by Django 5.0.2 on 2024-02-28 09:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0005_cartitem_selected_extra_ids_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together=set(),
        ),
    ]
