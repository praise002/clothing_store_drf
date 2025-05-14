from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from apps.common.serializers import SuccessResponseSerializer
from apps.orders.models import OrderItem
from .models import Category, Product, Review, Wishlist
from drf_spectacular.utils import extend_schema_field


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    """

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "customer",
            "text",
            "rating",
            "image",
            "created",
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    """

    customer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "product",
            "text",
            "customer",  # customer will be logged in user
            "rating",  # 1-5
            "image",
        ]

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs["product"]

        # Check if user has purchased the product
        has_purchased = OrderItem.objects.filter(
            order__customer=user.profile,
            product=product,
            order__shipping_status="delivered",
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError(
                "You can only review products you have purchased."
            )

        # Check if user has already reviewed this product
        has_reviewed = Review.objects.filter(
            customer=user.profile, product=product
        ).exists()

        if has_reviewed:
            raise serializers.ValidationError("You have already reviewed this product.")

        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["text", "rating", "image"]

    def validate(self, attrs):
        instance = self.instance
        # Ensure the user can only update their own review
        if instance and instance.customer != self.context["request"].user.profile:
            raise PermissionDenied("You don't have permission to update this review.")
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    cropped_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "price",
            "discounted_price",
            "in_stock",
            "is_available",
            "featured",
            "flash_deals",
            "avg_rating",
            "image_url",
            "cropped_image_url",
        ]

    @extend_schema_field(serializers.URLField)
    def get_cropped_image_url(self, obj):
        return obj.get_cropped_image_url()


class ProductWithReviewsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    cropped_image_url = serializers.SerializerMethodField(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "price",
            "discounted_price",
            "in_stock",
            "is_available",
            "featured",
            "flash_deals",
            "avg_rating",
            "num_of_reviews",
            "image_url",
            "cropped_image_url",
            "reviews",
        ]

    @extend_schema_field(serializers.URLField)
    def get_cropped_image_url(self, obj):
        return obj.get_cropped_image_url()


class ProductAddSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    cropped_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "price",
            "discounted_price",
            "in_stock",
            "is_available",
            "image_url",
            "cropped_image_url",
        ]

    @extend_schema_field(serializers.URLField)
    def get_cropped_image_url(self, obj):
        return obj.get_cropped_image_url()


class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for the Wishlist model.
    """

    products = ProductSerializer(read_only=True, many=True)
    profile = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            "id",
            "profile",
            "products",
        ]


# RESPONSES
class CategoryResponseSerializer(SuccessResponseSerializer):
    data = CategorySerializer()


class ProductResponseSerializer(SuccessResponseSerializer):
    data = ProductSerializer()


class ProductWithReviewsResponseSerializer(SuccessResponseSerializer):
    data = ProductWithReviewsSerializer()


class WishlistResponseSerializer(SuccessResponseSerializer):
    data = WishlistSerializer()


class ReviewResponseSerializer(SuccessResponseSerializer):
    data = ReviewSerializer()
