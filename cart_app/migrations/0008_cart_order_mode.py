# Generated by Django 5.0.2 on 2024-03-02 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0007_alter_cart_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='order_mode',
            field=models.CharField(choices=[('delivery', 'Delivery'), ('pick_up', 'Pick Up'), ('dine_in', 'Dine In')], default='delivery', max_length=20),
        ),
    ]
