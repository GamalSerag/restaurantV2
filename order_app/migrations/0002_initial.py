# Generated by Django 5.0.1 on 2024-01-21 07:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer_app', '0001_initial'),
        ('order_app', '0001_initial'),
        ('payment_app', '0001_initial'),
        ('restaurant_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_way',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment_app.paymentway'),
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order_app.order'),
        ),
        migrations.AddField(
            model_name='orderinvoice',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order_app.order'),
        ),
        migrations.AddField(
            model_name='orderinvoice',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant_app.restaurant'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer_app.customer'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant_app.restaurant'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='restaurant_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant_app.restauranttable'),
        ),
    ]
