from rest_framework.generics import ListAPIView, RetrieveAPIView

class CategoryListView(ListAPIView):
    """
    View to list all categories using ListAPIView.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class CategoryProductsView(RetrieveAPIView):
    """
    View to list products in a specific category using RetrieveAPIView.
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        slug = self.kwargs["slug"]
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise Http404("Category not found.")
        return category.products.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)
    
class ProductListView(ListAPIView):
    """
    View to list all products using ListAPIView.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
from rest_framework.generics import RetrieveAPIView, UpdateAPIView

class WishlistView(RetrieveAPIView):
    """
    View to retrieve the wishlist using RetrieveAPIView.
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(profile=self.request.user.profile)
        return wishlist

class WishlistUpdateView(UpdateAPIView):
    """
    View to add/remove products from the wishlist using UpdateAPIView.
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(profile=self.request.user.profile)
        return wishlist

    def perform_update(self, serializer):
        action = self.request.data.get("action")  # "add" or "remove"
        product_id = self.request.data.get("product_id")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise Http404("Product not found.")
        wishlist = self.get_object()
        if action == "add":
            wishlist.products.add(product)
        elif action == "remove":
            wishlist.products.remove(product)
        serializer.save()
        
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Category
from .serializers import CategorySerializer

class CategoryRetrieveView(RetrieveAPIView):
    """
    View to retrieve a single category by its slug using RetrieveAPIView.
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"  # Use 'slug' instead of the default 'pk'

    def get_queryset(self):
        return Category.objects.all()

    @extend_schema(
        summary="Retrieve a category",
        description="This endpoint retrieves a single category by its slug.",
        tags=tags,
        responses={
            200: CategorySerializer,
            404: "Category not found",
            401: "Unauthorized",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Product
from .serializers import ProductSerializer

class ProductRetrieveView(RetrieveAPIView):
    """
    View to retrieve a single product by its ID using RetrieveAPIView.
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"  # Default is 'pk', but explicitly specifying 'id' for clarity

    def get_queryset(self):
        return Product.objects.all()

    @extend_schema(
        summary="Retrieve a product",
        description="This endpoint retrieves a single product by its ID.",
        tags=tags,
        responses={
            200: ProductSerializer,
            404: "Product not found",
            401: "Unauthorized",
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
from django.urls import path
from .views import (
    CategoryRetrieveView as CategoryRetrieveAPIView,
    ProductRetrieveView as ProductRetrieveAPIView,
)

urlpatterns = [
    # APIView Versions
    path('api/v1/categories/<slug:slug>/', CategoryRetrieveAPIView.as_view(), name='category-retrieve'),
    path('api/v1/products/<int:pk>/', ProductRetrieveAPIView.as_view(), name='product-retrieve'),

    # Concrete View Class Versions
    path('api/v1/categories/<slug:slug>/retrieve/', CategoryRetrieveView.as_view(), name='category-retrieve-generic'),
    path('api/v1/products/<int:pk>/retrieve/', ProductRetrieveView.as_view(), name='product-retrieve-generic'),
]