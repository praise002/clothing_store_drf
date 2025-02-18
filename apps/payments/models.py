from django.db import models

class PaymentEvent(models.Model):
    event_id = models.CharField(max_length=100, unique=True)  # Flutterwave event ID
    status = models.CharField(max_length=50)  # Payment status (e.g., "successful")
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Payment amount
    currency = models.CharField(max_length=3)  # Payment currency (e.g., "NGN")
    transaction_id = models.CharField(max_length=100)  # Flutterwave transaction ID
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"PaymentEvent {self.event_id} ({self.status})"
