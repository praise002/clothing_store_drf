from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
)
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from apps.common.pagination import CustomPagination, DefaultPagination
from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)

from apps.shop.filters import ProductFilter
from .models import Category, Product, Review, Wishlist
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductWithReviewsSerializer,
    ReviewCreateSerializer,
    ReviewSerializer,
    ReviewUpdateSerializer,
    WishlistSerializer,
)

tags = ["Shop"]

review_tags = ["reviews"]


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
            200: CategorySerializer,
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
            200: ProductSerializer,
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
        products = Product.objects.available().filter(category=category)
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
            200: ProductSerializer,
        },
        operation_id="list_all_products",  # Unique operationId
        auth=[],
    )
    def get(self, request):
        products = Product.objects.available()
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
            200: ProductSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
        },
        auth=[],
    )
    def get(self, request, pk, slug):
        try:
            product = Product.objects.select_related("category").get(
                id=pk,
                slug=slug,
                in_stock__gt=0,
                is_available=True,
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.serializer_class(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductReviewsRetrieveView(APIView):
    serializer_class = ProductWithReviewsSerializer

    @extend_schema(
        summary="Retrieve a specific product by ID and slug with reviews",
        description="This endpoint retrieves a specific product using its ID and slug with its reviews.",
        tags=review_tags,
        responses={
            200: ProductWithReviewsSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
        },
        auth=[],
    )
    def get(self, request, pk, slug):
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
            200: WishlistSerializer,
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
            200: WishlistSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        request=None,  # No request body
    )
    def post(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(profile=request.user.profile)

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


class ReviewCreateView(APIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create a product review",
        description="This endpoint allows authenticated users to create product reviews.",
        tags=review_tags,
        responses={
            201: ReviewCreateSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # Add the authenticated user as the reviewer
        updated_instance = serializer.save(
            customer=request.user.profile
        )  # Save the updated instance

        # Serialize the created review for the response
        review_serializer = ReviewSerializer(updated_instance)  # Re-serialize

        return Response(
            {"message": "Review created successfully.", "data": review_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class ReviewUpdateDestroyView(APIView):
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        # Retrieve a specific review
        try:
            return Review.objects.get(id=pk)
        except Review.DoesNotExist:
            return Response(
                {"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Update a product review",
        description="This endpoint allows authenticated users to update their own product reviews.",
        tags=review_tags,
        responses={
            200: ReviewUpdateSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def patch(self, request, pk):
        review = self.get_object(pk)

        serializer = self.serializer_class(
            review, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Review updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a product review",
        description="This endpoint allows authenticated users to delete their own product reviews.",
        tags=review_tags,
        responses={
            204: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, pk):
        """
        Delete a specific review.
        """
        review = self.get_object(pk)

        # Delete the review
        review.delete()

        return Response(
            {"message": "Review deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
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
            200: ProductSerializer,
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
            200: ProductSerializer,
        },
        operation_id="list_all_products",  # Unique operationId
        auth=[],
    )
    def get(self, request):
        return super().get(request)


class ProductRetrieveGenericView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related("category").filter(
        in_stock__gt=0, is_available=True
    )

    @extend_schema(
        summary="Retrieve a specific product by ID and slug",
        description="This endpoint retrieves a specific product using its ID and slug.",
        tags=tags,
        responses={
            200: ProductSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
        },
        auth=[],
    )
    def get(self, request, *args, **kwargs):
        """
        Override the get method to customize the response format.
        """
        return super().get(request, *args, **kwargs)

    def get_object(self):
        """
        Retrieve the product instance using both `pk` and `slug`.
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwargs = self.lookup_url_kwargs or self.lookup_field

        # Extract `pk` and `slug` from the URL kwargs
        pk = self.kwargs.get(lookup_url_kwargs)
        slug = self.kwargs.get("slug")

        try:
            # Filter the product by both `pk` and `slug`
            obj = queryset.get(id=pk, slug=slug)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Return the retrieved object
        self.check_object_permissions(self.request, obj)
        return obj


class ProductReviewsRetrieveGenericView(RetrieveAPIView):
    serializer_class = ProductWithReviewsSerializer
    queryset = (
        Product.objects.select_related("category")
        .prefetch_related("reviews", "reviews__customer")
        .filter(in_stock__gt=0, is_available=True)
    )

    @extend_schema(
        summary="Retrieve a specific product by ID and slug with reviews",
        description="This endpoint retrieves a specific product using its ID and slug with its reviews.",
        tags=review_tags,
        responses={
            200: ProductWithReviewsSerializer,
            404: ErrorResponseSerializer,
        },
        auth=[],
    )
    def get(self, request, *args, **kwargs):
        """
        Override the get method to customize the response format.
        """
        return super().get(request, *args, **kwargs)

    def get_object(self):
        """
        Retrieve the product instance using both `pk` and `slug`.
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwargs = self.lookup_url_kwargs or self.lookup_field

        # Extract `pk` and `slug` from the URL kwargs
        pk = self.kwargs.get(lookup_url_kwargs)
        slug = self.kwargs.get("slug")

        try:
            # Filter the product by both `pk` and `slug`
            obj = queryset.get(id=pk, slug=slug)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Return the retrieved object
        self.check_object_permissions(self.request, obj)
        return obj


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
            200: WishlistSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        return super().get(request)


class ReviewCreateGenericAPIView(CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create a product review",
        description="This endpoint allows authenticated users to create product reviews.",
        tags=review_tags,
        responses={
            201: ReviewCreateSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Override the create method to customize the response format.
        """
        # Pass the request to the serializer context
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # Save the review with the authenticated user as the reviewer
        self.perform_create(serializer)

        # Serialize the created review for the response
        review = serializer.instance
        review_serializer = ReviewSerializer(review)

        return Response(
            {
                "message": "Review created successfully.",
                "data": review_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        """
        Perform the actual creation of the review, associating it with the authenticated user.
        """
        serializer.save(customer=self.request.user.profile)
