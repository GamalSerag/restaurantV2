# Generated by Django 5.0.2 on 2024-03-11 11:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0014_rename_buisness_register_admindoc_business_register'),
    ]

    operations = [
        migrations.RenameField(
            model_name='admindoc',
            old_name='adress',
            new_name='address',
        ),
    ]
