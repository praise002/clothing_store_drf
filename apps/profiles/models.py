from django.db import models
from django.conf import settings

from apps.common.models import BaseModel


class NigerianStates(models.TextChoices):
    ABIA = "Abia", "Abia"
    ADAMAWA = "Adamawa", "Adamawa"
    AKWA_IBOM = "Akwa Ibom", "Akwa Ibom"
    ANAMBRA = "Anambra", "Anambra"
    BAUCHI = "Bauchi", "Bauchi"
    BAYELSA = "Bayelsa", "Bayelsa"
    BENUE = "Benue", "Benue"
    BORNO = "Borno", "Borno"
    CROSS_RIVER = "Cross River", "Cross River"
    DELTA = "Delta", "Delta"
    EBONYI = "Ebonyi", "Ebonyi"
    EDO = "Edo", "Edo"
    EKITI = "Ekiti", "Ekiti"
    ENUGU = "Enugu", "Enugu"
    GOMBE = "Gombe", "Gombe"
    IMO = "Imo", "Imo"
    JIGAWA = "Jigawa", "Jigawa"
    KADUNA = "Kaduna", "Kaduna"
    KANO = "Kano", "Kano"
    KATSINA = "Katsina", "Katsina"
    KEBBI = "Kebbi", "Kebbi"
    KOGI = "Kogi", "Kogi"
    KWARA = "Kwara", "Kwara"
    LAGOS = "Lagos", "Lagos"
    NASARAWA = "Nasarawa", "Nasarawa"
    NIGER = "Niger", "Niger"
    OGUN = "Ogun", "Ogun"
    ONDO = "Ondo", "Ondo"
    OSUN = "Osun", "Osun"
    OYO = "Oyo", "Oyo"
    PLATEAU = "Plateau", "Plateau"
    RIVERS = "Rivers", "Rivers"
    SOKOTO = "Sokoto", "Sokoto"
    TARABA = "Taraba", "Taraba"
    YOBE = "Yobe", "Yobe"
    ZAMFARA = "Zamfara", "Zamfara"
    FCT = "FCT", "FCT"


class ShippingFee(models.Model):
    state = models.CharField(
        max_length=20,
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
        max_length=20,
        choices=NigerianStates.choices,
    )
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    shipping_fee = models.PositiveIntegerField(
        default=0
    )  # This will be updated dynamically
    shipping_time = models.CharField(max_length=50, default="1-3 business days")
    user = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, related_name="shipping_addresses"
    )
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

        if self.default:
            # Find all other addresses for this user that are currently default
            # and set them to not be default
            ShippingAddress.objects.filter(
                user=self.user,  # Only addresses for this user
                default=True,  # That are currently marked as default
            ).exclude(
                pk=self.pk  # Exclude this address itself (important for updates)
            ).update(
                default=False
            )  # Set them all to not be default

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # If this is the default address, throw an error
        if self.default:
            raise ValueError("Cannot delete default shipping address")

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.state} - ₦{self.shipping_fee}"
    
    class Meta:
        verbose_name_plural = "Shipping Addresses"


class Profile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        editable=False,
    )
    avatar = models.ImageField(upload_to="avatars/", null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"{self.user.full_name}"

    @property
    def avatar_url(self):
        try:
            url = self.avatar.url
        except:
            url = "https://res.cloudinary.com/dq0ow9lxw/image/upload/v1732236186/default-image_foxagq.jpg"
        return url
