# from django.db import models
# from django.core.validators import MaxValueValidator, MinValueValidator
# from django.utils.timezone import now

# from apps.profiles.models import Profile


# class Coupon(models.Model):
#     code = models.CharField(max_length=50, unique=True)
#     valid_from = models.DateTimeField()
#     valid_to = models.DateTimeField()
#     discount = models.SmallIntegerField(
#         validators=[MinValueValidator(0), MaxValueValidator(100)],
#         help_text="Percentage value (0 to 100)",
#     )
#     active = models.BooleanField(default=True)
    
#     def __str__(self):
#         return self.code

# class CouponUsage(models.Model):
#     profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
#     coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
#     redeemed_at = models.DateTimeField(default=now)
    
#     def __str__(self):
#         return f'{self.profile} - {self.coupon}'

#     class Meta:
#         unique_together = ('profile', 'coupon')  # Ensure a user can only redeem the coupon once
        

