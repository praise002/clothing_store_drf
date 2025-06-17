from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.errors import ErrorCode
from apps.common.exceptions import NotFoundError
from apps.common.pagination import CustomPagination, DefaultPagination
from apps.common.responses import CustomResponse
from apps.shop.filters import ProductFilter
from apps.shop.schema_examples import (
    CATEGORY_LIST_RESPONSE,
    CATEGORY_PRODUCT_LIST_RESPONSE,
    PRODUCT_LIST_RESPONSE,
    PRODUCT_RETRIEVE_RESPONSE,
    PRODUCT_REVIEW_RETRIEVE_RESPONSE,
    REVIEW_CREATE_RESPONSE,
    REVIEW_DELETE_RESPONSE,
    REVIEW_UPDATE_RESPONSE,
    WISHLIST_ADD_PRODUCT_RESPONSE,
    WISHLIST_REMOVE_PRODUCT_RESPONSE,
    WISHLIST_RESPONSE,
)

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
        responses=CATEGORY_LIST_RESPONSE,
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
        responses=CATEGORY_PRODUCT_LIST_RESPONSE,
        auth=[],
    )
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise NotFoundError(
                err_msg="Category does not exist.",
            )

        # products = category.products.all()
        products = (
            Product.objects.available()
            .filter(category=category)
            .select_related("category")
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
        responses=PRODUCT_LIST_RESPONSE,
        operation_id="list_all_products",  # Unique operationId
        auth=[],
    )
    def get(self, request):
        products = (
            Product.objects.available()
            .select_related("category")
            .prefetch_related("reviews")
        )
        # products = Product.objects.available()
        serializer = self.serializer_class(products, many=True)
        return CustomResponse.success(
            message="Products retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ProductRetrieveView(APIView):
    """
    View to retrieve a single product by its ID.
    """

    serializer_class = ProductSerializer

    @extend_schema(
        summary="Retrieve a specific product by ID and slug",
        description="This endpoint retrieves a specific product using its ID and slug.",
        tags=tags,
        responses=PRODUCT_RETRIEVE_RESPONSE,
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
            raise NotFoundError(
                err_msg="Product not found.",
            )

        serializer = self.serializer_class(product)
        return CustomResponse.success(
            message="Product retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ProductReviewsRetrieveView(APIView):
    serializer_class = ProductWithReviewsSerializer

    @extend_schema(
        summary="Retrieve a specific product by ID and slug with reviews",
        description="This endpoint retrieves a specific product using its ID and slug with its reviews.",
        tags=review_tags,
        responses=PRODUCT_REVIEW_RETRIEVE_RESPONSE,
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
            raise NotFoundError(
                err_msg="Product not found.",
            )

        serializer = self.serializer_class(product)
        return CustomResponse.success(
            message="Product retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


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
        responses=WISHLIST_RESPONSE,
    )
    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(profile=request.user.profile)
        serializer = self.serializer_class(wishlist)
        return CustomResponse.success(
            message="Wishlist retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class WishlistUpdateDestroyView(APIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add to wishlist",
        description="This endpoint adds a product to the wishlist of the authenticated user.",
        tags=tags,
        responses=WISHLIST_ADD_PRODUCT_RESPONSE,
        request=None,  # No request body
    )
    def post(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(profile=request.user.profile)

        try:
            product = Product.objects.get(
                id=product_id, is_available=True, in_stock__gt=0
            )
        except Product.DoesNotExist:
            raise NotFoundError(
                err_msg="Product not found.",
            )

        if product in wishlist.products.all():
            return CustomResponse.error(
                message="Product already in wishlist.",
                status_code=status.HTTP_409_CONFLICT,
                err_code=ErrorCode.ALREADY_EXISTS,
            )
        wishlist.products.add(product)
        return CustomResponse.success(
            message="Product added to wishlist.", status_code=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Remove from wishlist",
        description="This endpoint removes a product from the wishlist of the authenticated user.",
        tags=tags,
        responses=WISHLIST_REMOVE_PRODUCT_RESPONSE,
    )
    def delete(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(profile=request.user.profile)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFoundError(
                err_msg="Product not found.",
            )

        if product not in wishlist.products.all():
            return CustomResponse.error(
                message="Product not in wishlist.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                err_code=ErrorCode.BAD_REQUEST,
            )
        wishlist.products.remove(product)
        return CustomResponse.success(
            message="Product removed from wishlist.", status_code=status.HTTP_200_OK
        )


class ReviewCreateView(APIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create a product review",
        description="This endpoint allows authenticated users to create product reviews.",
        tags=review_tags,
        responses=REVIEW_CREATE_RESPONSE,
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

        return CustomResponse.success(
            message="Review created successfully.",
            data=review_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )


class ReviewUpdateDestroyView(APIView):
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        # Retrieve a specific review
        try:
            return Review.objects.get(id=pk)
        except Review.DoesNotExist:
            raise NotFoundError(
                err_msg="Review not found.",
            )

    @extend_schema(
        summary="Update a product review",
        description="This endpoint allows authenticated users to update their own product reviews.",
        tags=review_tags,
        responses=REVIEW_UPDATE_RESPONSE,
    )
    def patch(self, request, pk):
        review = self.get_object(pk)

        serializer = self.serializer_class(
            review, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        # Serialize the updated review for the response
        review_serializer = ReviewSerializer(updated_instance)  # Re-serialize

        return CustomResponse.success(
            message="Review updated successfully.",
            data=review_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a product review",
        description="This endpoint allows authenticated users to delete their own product reviews.",
        tags=review_tags,
        responses=REVIEW_DELETE_RESPONSE,
    )
    def delete(self, request, pk):
        """
        Delete a specific review.
        """
        review = self.get_object(pk)

        if review.customer != self.request.user:
            return CustomResponse.error(
                message="You don't have permission to delete this review.",
                status_code=status.HTTP_403_FORBIDDEN,
                err_code=ErrorCode.FORBIDDEN,
            )

        # Delete the review
        review.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
        responses=CATEGORY_LIST_RESPONSE,
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
            raise NotFoundError(
                err_msg="Category does not exist.",
            )

        products = (
            Product.objects.available()
            .filter(category=category_instance)
            .select_related("category")
            .prefetch_related("reviews")
        )
        return products

    @extend_schema(
        summary="List products in a category",
        description="This endpoint retrieves all products belonging to a specific category.",
        tags=tags,
        responses=CATEGORY_PRODUCT_LIST_RESPONSE,
        auth=[],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, many=True)
        return CustomResponse.success(
            message="Products retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ProductListGenericView(ListAPIView):
    """
    View to list all products using ListAPIView.
    """

    queryset = (
        Product.objects.available()
        .select_related("category")
        .prefetch_related("reviews")
    )
    serializer_class = ProductSerializer
    pagination_class = DefaultPagination
    filterset_class = ProductFilter
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ["name", "description"]

    @extend_schema(
        summary="List all available products",
        description="This endpoint retrieves a list of all available products.",
        tags=tags,
        responses=PRODUCT_LIST_RESPONSE,
        operation_id="list_all_products",  # Unique operationId
        auth=[],
    )
    def get(self, request):
        return super().get(request)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message="Products retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ProductRetrieveGenericView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related("category").filter(
        in_stock__gt=0, is_available=True
    )

    @extend_schema(
        summary="Retrieve a specific product by ID and slug",
        description="This endpoint retrieves a specific product using its ID and slug.",
        tags=tags,
        responses=PRODUCT_RETRIEVE_RESPONSE,
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
            raise NotFoundError(
                err_msg="Product not found.",
            )

        # Return the retrieved object
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(
            message="Product retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


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
        responses=PRODUCT_REVIEW_RETRIEVE_RESPONSE,
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
            raise NotFoundError(
                err_msg="Product not found.",
            )

        # Return the retrieved object
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(
            message="Product retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


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
        responses=WISHLIST_RESPONSE,
    )
    def get(self, request):
        return super().get(request)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(
            message="Wishlist retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ReviewCreateGenericAPIView(CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create a product review",
        description="This endpoint allows authenticated users to create product reviews.",
        tags=review_tags,
        responses=REVIEW_CREATE_RESPONSE,
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

        return CustomResponse.success(
            message="Review created successfully.",
            data=review_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        """
        Perform the actual creation of the review, associating it with the authenticated user.
        """
        serializer.save(customer=self.request.user.profile)
