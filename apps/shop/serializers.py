from rest_framework import serializers
from .models import Category, Product, Review, Wishlist


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
            "created",
        ]
        # read_only_fields = ["id", "customer", "customer_name", "created"]


class ProductSerializer(serializers.ModelSerializer):
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
            "profile", #TODO: NOT SHOWING, return in view
            "products",
        ]
        # read_only_fields = ["profile", "products"]
