from cloudinary.models import CloudinaryField
from django.db import models
from django.forms import ValidationError

from apps.common.models import BaseModel

TEAM_MEMBER_FOLDER = "team/"


class Social(models.Model):
    fb = models.URLField(blank=True, null=True)
    tw = models.URLField(blank=True, null=True)
    ln = models.URLField(blank=True, null=True)
    ig = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SiteDetail(BaseModel):
    name = models.CharField(max_length=255, default="Clothing Store")
    description = models.TextField(
        default="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum"
    )
    phone = models.CharField(max_length=20, default="+2348029874990")
    address = models.CharField(max_length=500, default="Lagos, Nigeria")
    email = models.EmailField(default="praizthecoder@gmail.com")
    company_socials = models.OneToOneField(Social, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding and SiteDetail.objects.exists():
            raise ValidationError("Only one site detail object can be created.")
        return super(SiteDetail, self).save(*args, **kwargs)


class TeamMember(BaseModel):
    ROLE_CHOICES = (
        ("CO-Founder", "CO-Founder"),
        ("Product Expert", "Product Expert"),
        ("Chief Marketing", "Chief Marketing"),
        ("Product Specialist", "Product Specialist"),
        ("Product Photographer", "Product Photographer"),
        ("General Manager", "General Manager"),
    )
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    description = models.TextField()
    avatar = CloudinaryField("image", folder=TEAM_MEMBER_FOLDER)
    social_links = models.OneToOneField(Social, on_delete=models.SET_NULL, null=True)

    @property
    def avatar_url(self):
        return self.avatar.url


class Message(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created"]
