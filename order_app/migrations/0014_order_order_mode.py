# Generated by Django 5.0.1 on 2024-03-27 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0013_order_payment_intent_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_mode',
            field=models.CharField(default='delivery', max_length=20),
            preserve_default=False,
        ),
    ]
