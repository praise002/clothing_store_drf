# Generated by Django 5.1.5 on 2025-05-11 20:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0001_initial'),
        ('shop', '0006_alter_product_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productdiscount',
            name='product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='discount', to='shop.product'),
        ),
    ]
