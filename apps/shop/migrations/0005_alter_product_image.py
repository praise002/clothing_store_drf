# Generated by Django 5.1.5 on 2025-03-11 09:46

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_alter_review_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
    ]
