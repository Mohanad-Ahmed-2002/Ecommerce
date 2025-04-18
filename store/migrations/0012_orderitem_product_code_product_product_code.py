# Generated by Django 5.2 on 2025-04-07 08:23

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_remove_customerorder_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='product_code',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='product_code',
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
    ]
