# Generated by Django 5.0.1 on 2024-01-21 07:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer_app', '0001_initial'),
        ('restaurant_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartMenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamps', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('special_instructions', models.TextField(blank=True, null=True)),
                ('saus', models.JSONField(blank=True, null=True)),
                ('size', models.JSONField(blank=True, null=True)),
                ('categories', models.ManyToManyField(to='restaurant_app.category')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant_app.menuitem')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamps', models.DateTimeField(auto_now_add=True)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('notes', models.TextField(blank=True, null=True)),
                ('service', models.CharField(max_length=255)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer')),
                ('cart_items', models.ManyToManyField(related_name='carts', to='cart_app.cartmenuitem')),
            ],
        ),
    ]
