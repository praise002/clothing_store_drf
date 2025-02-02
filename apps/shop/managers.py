from django.db import models


class ProductManager(models.Manager):
    def available(self):
        """
        Return products that are in stock and available.
        """
        return self.get_queryset().filter(in_stock__gt=0, is_available=True)
