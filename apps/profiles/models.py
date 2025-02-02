from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shipping_address = models.CharField(_("Shipping Address"), max_length=100)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    avatar = models.ImageField(
        _("Avatar"), upload_to="photos/%Y/%m/%d/", null=True, blank=True
    )
    phone = models.CharField(_("Phone"), max_length=100)
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
