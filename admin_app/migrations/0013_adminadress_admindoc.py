# Generated by Django 5.0.2 on 2024-03-11 09:28

import admin_app.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_app', '0012_admin_is_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAdress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line1', models.CharField()),
                ('postal_code', models.CharField()),
                ('city', models.CharField()),
            ],
        ),
        migrations.CreateModel(
            name='AdminDoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leagal_name', models.CharField()),
                ('ID_photo', models.FileField(upload_to=admin_app.models.admin_docs_image_path)),
                ('buisness_register', models.FileField(upload_to=admin_app.models.admin_docs_image_path)),
                ('adress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_app.adminadress')),
            ],
        ),
    ]
