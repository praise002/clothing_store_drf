# Generated by Django 5.1.5 on 2025-03-02 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_order_pending_email_sent_alter_order_payment_status'),
        ('profiles', '0006_alter_shippingaddress_state_alter_shippingfee_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='in_transit_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='processing_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'pending'), ('successfull', 'successfull'), ('cancelled', 'cancelled'), ('refunded', 'refunded')], default='pending', max_length=20),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['payment_status', 'pending_email_sent'], name='orders_orde_payment_84a561_idx'),
        ),
    ]
