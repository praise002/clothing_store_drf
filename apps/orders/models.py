from decimal import Decimal
from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.common.models import BaseModel
# from apps.coupons.models import Coupon
from apps.profiles.models import Profile
from apps.shop.models import Product

# class Delivery(models.Model):
#     fee = models.PositiveSmallIntegerField(default=3000)
#     delivery_time = models.CharField(max_length=50, default="1-3 business days")  

#     class Meta:
#         verbose_name = "Delivery"
#         verbose_name_plural = "Deliveries"

#     def __str__(self):
#         return f"{self.delivery_time} - Fee: {self.fee}"
    
class Order(BaseModel):
    # Shipping status
    SHIPPING_STATUS_PENDING = "P"
    SHIPPING_STATUS_SHIPPED = "S"
    SHIPPING_STATUS_DELIVERED = "D"

    SHIPPING_STATUS_CHOICES = [
        (SHIPPING_STATUS_PENDING, "PENDING"),
        (SHIPPING_STATUS_SHIPPED, "SHIPPED"),
        (SHIPPING_STATUS_DELIVERED, "DELIVERED"),
    ]

    customer = models.ForeignKey(
        Profile, on_delete=models.PROTECT, related_name="orders"
    )
    paid = models.BooleanField(default=False)
    shipping_status = models.CharField(
        max_length=1, choices=SHIPPING_STATUS_CHOICES, blank=True
    ) # i will put it to pending if payment was successful
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_ref = models.CharField(max_length=15, blank=True)
    # coupon = models.ForeignKey(
    #     Coupon, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL
    # )
    # discount = models.SmallIntegerField(
    #     default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    # )  # if coupon gets deleted. order is preserved
    # delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, blank=True)
    # delivery_fee = models.PositiveSmallIntegerField(
    #     default=0
    # )  # if delivery gets deleted. order is preserved
    
    class Meta:
        ordering = ["-placed_at"]
        indexes = [
            models.Index(fields=["-placed_at"]),
        ]

    def __str__(self):
        return f"Order {self.id} by {self.customer.user.full_name}"

    # def get_total_cost(self):
    #     total_cost = self.get_total_cost_before_discount() 
    #     return total_cost - self.get_discount() 

    # def get_total_cost_before_discount(self):
    #     return sum(item.get_cost() for item in self.items.all()) + self.delivery_fee

    # def get_discount(self):
    #     total_cost = self.get_total_cost_before_discount()
    #     if self.discount:
    #         return total_cost * (self.discount / Decimal(100))
    #     return Decimal(0)
    

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.product} in order {self.order.id}"
