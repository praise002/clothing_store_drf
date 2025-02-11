from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from apps.common.pagination import CustomPagination, DefaultPagination
from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from apps.common.validators import validate_uuid
from apps.shop.filters import ProductFilter
from .models import Category, Product, Wishlist
from .serializers import CategorySerializer, ProductSerializer, WishlistSerializer

tags = ["Shop"]


class CategoryListView(APIView):
    """
    View to list all categories.
    """

    serializer_class = CategorySerializer
    paginator_class = CustomPagination()
    paginator_class.page_size = 10

    @extend_schema(
        summary="List all categories",
        description="This endpoint retrieves a list of all product categories.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
        },
        auth=[],
    )
    def get(self, request):
        categories = Category.objects.all()
        paginated_categories = self.paginator_class.paginate_queryset(
            categories, request
        )
        serializer = self.serializer_class(paginated_categories, many=True)

        return self.paginator_class.get_paginated_response(serializer.data)


class CategoryProductsView(APIView):
    """
    View to list products in a specific category.
    """

    serializer_class = ProductSerializer
    paginator_class = CustomPagination()
    paginator_class.page_size = 10

    @extend_schema(
        summary="List products in a category",
        description="This endpoint retrieves all products belonging to a specific category.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            404: ErrorResponseSerializer,
        },
        auth=[],
    )
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND
            )
        # products = category.products.all()
        products = (
            Product.objects.available()
            .filter(category=category)
            .prefetch_related("reviews")
        )
        paginated_products = self.paginator_class.paginate_queryset(products, request)
        serializer = self.serializer_class(paginated_products, many=True)

        return self.paginator_class.get_paginated_response(serializer.data)


class ProductListView(APIView):
    """
    View to list all products.
    """

    serializer_class = ProductSerializer

    @extend_schema(
        summary="List all available products",
        description="This endpoint retrieves a list of all available products.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
        },
        operation_id="list_all_products",  # Unique operationId
        auth=[],
    )
    def get(self, request):
        products = Product.objects.available().prefetch_related("reviews")
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductRetrieveView(APIView):
    """
    View to retrieve a single product by its ID.
    """

    serializer_class = ProductSerializer

    @extend_schema(
        summary="Retrieve a specific product by ID and slug",
        description="This endpoint retrieves a specific product using its ID and slug.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
        },
        auth=[],
    )
    def get(self, request, pk, slug):
        if not validate_uuid(pk):
            return Response(
                {"error": "Invalid product ID."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = (
                Product.objects.select_related("category")
                .prefetch_related("reviews", "reviews__customer")
                .get(
                    id=pk,
                    slug=slug,
                    in_stock__gt=0,
                    is_available=True,
                )
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.serializer_class(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WishlistView(APIView):
    """
    View to manage the wishlist.
    """

    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List wishlist",
        description="This endpoint retrieves the wishlist of the authenticated user.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(profile=request.user.profile)
        serializer = self.serializer_class(wishlist)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WishlistUpdateDestroyView(APIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add to wishlist",
        description="This endpoint adds a product to the wishlist of the authenticated user.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        request=None,  # No request body
    )
    def post(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(profile=request.user.profile)

        if not validate_uuid(product_id):
            return Response(
                {"error": "Invalid product ID."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(
                id=product_id, is_available=True, in_stock__gt=0
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if product in wishlist.products.all():
            return Response(
                {"error": "Product already in wishlist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        wishlist.products.add(product)
        return Response(
            {
                "message": "Product added to wishlist.",
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Remove from wishlist",
        description="This endpoint removes a product from the wishlist of the authenticated user.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def delete(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(profile=request.user.profile)
        if not validate_uuid(product_id):
            return Response(
                {"error": "Invalid product ID."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if product not in wishlist.products.all():
            return Response(
                {"error": "Product not in wishlist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        wishlist.products.remove(product)
        return Response(
            {"message": "Product removed from wishlist."}, status=status.HTTP_200_OK
        )


# Generic version
class CategoryListGenericView(ListAPIView):
    """
    View to list all categories using ListAPIView.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = DefaultPagination

    @extend_schema(
        summary="List all categories",
        description="This endpoint retrieves a list of all product categories.",
        tags=tags,
        responses={
            200: CategorySerializer,
            401: ErrorResponseSerializer,
        },
        auth=[],
    )
    def get(self, request):
        return super().get(request)


class CategoryProductsGenericView(RetrieveAPIView):
    """
    View to list products in a specific category using RetrieveAPIView.
    """

    serializer_class = ProductSerializer
    pagination_class = DefaultPagination

    def get_object(self):
        category = self.kwargs.get("slug")
        try:
            category_instance = Category.objects.get(slug=category)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND
            )
        products = (
            Product.objects.available()
            .filter(category=category_instance)
            .prefetch_related("reviews")
        )
        return products

    @extend_schema(
        summary="List products in a category",
        description="This endpoint retrieves all products belonging to a specific category.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            404: ErrorResponseSerializer,
        },
        auth=[],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)


class ProductListGenericView(ListAPIView):
    """
    View to list all products using ListAPIView.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = DefaultPagination
    filterset_class = ProductFilter
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ["name", "description"]

    @extend_schema(
        summary="List all available products",
        description="This endpoint retrieves a list of all available products.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
        },
        operation_id="list_all_products",  # Unique operationId
        auth=[],
    )
    def get(self, request):
        return super().get(request)


class WishlistGenericView(RetrieveAPIView):
    """
    View to retrieve the wishlist using RetrieveAPIView.
    """

    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wishlist, _ = Wishlist.objects.get_or_create(profile=self.request.user.profile)
        return wishlist

    @extend_schema(
        summary="List wishlist",
        description="This endpoint retrieves the wishlist of the authenticated user.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        return super().get(request)
