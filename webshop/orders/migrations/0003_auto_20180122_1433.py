# Generated by Django 2.0.1 on 2018-01-22 06:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20180122_1417'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='coupon',
        ),
        migrations.RemoveField(
            model_name='order',
            name='discount',
        ),
    ]