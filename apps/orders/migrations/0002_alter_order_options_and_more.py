# Generated by Django 5.1.5 on 2025-02-13 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
        ('profiles', '0004_shippingfee_remove_profile_state_remove_profile_city_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created']},
        ),
        migrations.RemoveIndex(
            model_name='order',
            name='orders_orde_placed__c426b5_idx',
        ),
        migrations.RemoveField(
            model_name='order',
            name='paid',
        ),
        migrations.RemoveField(
            model_name='order',
            name='placed_at',
        ),
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending', help_text='Current status of the order in the fulfillment process', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_fee',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='state',
            field=models.CharField(default='-'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='shipping_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('in_transit', 'In Transit'), ('delivered', 'Delivered')], default='pending', max_length=20),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['-created'], name='orders_orde_created_743fca_idx'),
        ),
    ]
