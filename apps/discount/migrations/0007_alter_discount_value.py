# Generated by Django 5.1.5 on 2025-05-13 13:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0006_alter_discount_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='value',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
