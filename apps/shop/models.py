from autoslug import AutoSlugField
from django.db import models

from typing import Optional
from apps.profiles.models import Profile
from apps.common.models import BaseModel
from django.utils.translation import gettext_lazy as _
from statistics import mean

from apps.common.validators import validate_file_size

from cloudinary.models import CloudinaryField
from cloudinary import CloudinaryImage

from apps.shop.managers import ProductManager


class Category(BaseModel):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", unique=True, always_update=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# NOTE: USE PERMSSIONS IN ADMIN TO PREVENT ACCIDENTAL DELETION OF PRODUCT


class Product(BaseModel):
    name = models.CharField(max_length=19)
    slug = AutoSlugField(populate_from="name", unique=True, always_update=True)
    description = models.TextField(max_length=255)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.SET_NULL, null=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # price_after_discount = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    flash_deals = models.BooleanField(default=False)
    image = CloudinaryField(
        "image", folder="products/", validators=[validate_file_size]
    )

    objects = ProductManager()

    def get_cropped_image_url(self, width=250, height=250):
        # Generate a cropped image URL using Cloudinary transformations
        return CloudinaryImage(self.image.public_id).build_url(
            width=width,
            height=height,
            crop="fill",
            gravity="auto",
        )

    def __str__(self):
        return self.name

    @property
    def num_of_reviews(self) -> Optional[int]:
        return self.reviews.count()

    @property
    def avg_rating(self) -> Optional[float]:
        reviews = [review.rating for review in self.reviews.all()]
        avg = 0
        if len(reviews) > 0:
            avg = round(mean(list(reviews)))  # Mean
        return avg

    @property
    def image_url(self) -> Optional[str]:
        return self.image.url

    class Meta:
        ordering = ["-created"]


class Review(BaseModel):
    RATING_CHOICES = ((5, 5), (4, 4), (3, 3), (2, 2), (1, 1))

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.SmallIntegerField(choices=RATING_CHOICES)
    image = CloudinaryField(
        "review_image",
        folder="reviews/",
        # validators=[validate_file_size],
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.customer.user.full_name} review on {self.product.name}"

    class Meta:
        ordering = ["-created"]


class Wishlist(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name="wishlists", blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.user.full_name} wishlist"
