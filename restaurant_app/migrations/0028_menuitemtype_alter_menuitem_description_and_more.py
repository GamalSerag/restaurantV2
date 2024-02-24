# Generated by Django 5.0.2 on 2024-02-24 08:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0027_menuitemextra_menuitem_extras_menuitemextraitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItemType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='description',
            field=models.TextField(max_length=250),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.CreateModel(
            name='MenuItemTypeItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='types', to='restaurant_app.menuitemextra')),
            ],
        ),
    ]
