# Generated by Django 5.1.5 on 2025-02-02 17:03

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('paid', models.BooleanField(default=False)),
                ('shipping_status', models.CharField(blank=True, choices=[('P', 'PENDING'), ('S', 'SHIPPED'), ('D', 'DELIVERED')], max_length=1)),
                ('placed_at', models.DateTimeField(auto_now_add=True)),
                ('payment_ref', models.CharField(blank=True, max_length=15)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='profiles.profile')),
            ],
            options={
                'ordering': ['-placed_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='shop.product')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['-placed_at'], name='orders_orde_placed__c426b5_idx'),
        ),
    ]
