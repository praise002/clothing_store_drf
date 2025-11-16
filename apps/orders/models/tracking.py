from django.db import models

from apps.orders.utils import generate_tracking_number

class TrackingNumber(models.Model):
    """
    A model to store unique tracking numbers for orders.
    """

    number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.number
    
    @staticmethod
    def generate_tracking_number():
        while True:
            tracking_number = generate_tracking_number()
            if not TrackingNumber.objects.filter(number=tracking_number).exists():
                return tracking_number
        
