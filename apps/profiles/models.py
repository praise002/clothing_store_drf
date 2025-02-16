from django.db import models
from django.conf import settings
from typing import Optional

from apps.common.models import BaseModel


class NigerianStates(models.TextChoices):
    ABIA = "AB", "Abia"
    ADAMAWA = "AD", "Adamawa"
    AKWA_IBOM = "AK", "Akwa Ibom"
    ANAMBRA = "AN", "Anambra"
    BAUCHI = "BA", "Bauchi"
    BAYELSA = "BY", "Bayelsa"
    BENUE = "BE", "Benue"
    BORNO = "BO", "Borno"
    CROSS_RIVER = "CR", "Cross River"
    DELTA = "DE", "Delta"
    EBONYI = "EB", "Ebonyi"
    EDO = "ED", "Edo"
    EKITI = "EK", "Ekiti"
    ENUGU = "EN", "Enugu"
    GOMBE = "GO", "Gombe"
    IMO = "IM", "Imo"
    JIGAWA = "JI", "Jigawa"
    KADUNA = "KD", "Kaduna"
    KANO = "KN", "Kano"
    KATSINA = "KT", "Katsina"
    KEBBI = "KE", "Kebbi"
    KOGI = "KO", "Kogi"
    KWARA = "KW", "Kwara"
    LAGOS = "LA", "Lagos"
    NASARAWA = "NA", "Nasarawa"
    NIGER = "NI", "Niger"
    OGUN = "OG", "Ogun"
    ONDO = "ON", "Ondo"
    OSUN = "OS", "Osun"
    OYO = "OY", "Oyo"
    PLATEAU = "PL", "Plateau"
    RIVERS = "RI", "Rivers"
    SOKOTO = "SO", "Sokoto"
    TARABA = "TA", "Taraba"
    YOBE = "YO", "Yobe"
    ZAMFARA = "ZA", "Zamfara"
    FCT = "FC", "Federal Capital Territory"


class ShippingFee(models.Model):
    state = models.CharField(
        max_length=2,
        choices=NigerianStates.choices,
        unique=True,  # Ensure each state has only one shipping fee
    )
    fee = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.state} - ₦{self.fee}"


# a customer can have more than one shipping address, they only need to # need to supply one when placing an order or use the default
class ShippingAddress(BaseModel):
    phone_number = models.CharField(max_length=100)
    state = models.CharField(
        max_length=2,
        choices=NigerianStates.choices,
    )
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    shipping_fee = models.PositiveIntegerField(
        default=0
    )  # This will be updated dynamically
    shipping_time = models.CharField(max_length=50, default="1-3 business days")
    user = models.ForeignKey("Profile", on_delete=models.CASCADE)
    default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Override the save method to dynamically set the shipping fee based on the state.
        """
        try:
            # Retrieve the shipping fee for the selected state
            shipping_fee_instance = ShippingFee.objects.get(state=self.state)
            self.shipping_fee = shipping_fee_instance.fee
        except ShippingFee.DoesNotExist:
            self.shipping_fee = 0  # Default to 0 if no fee is found

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.state} - ₦{self.shipping_fee}"


class Profile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False
    )
    avatar = models.ImageField(upload_to="photos/%Y/%m/%d/", null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"{self.user.full_name}"

    @property
    def avatar_url(self) -> Optional[str]:
        try:
            url = self.avatar.url
        except:
            url = "https://res.cloudinary.com/dq0ow9lxw/image/upload/v1732236186/default-image_foxagq.jpg"
        return url
