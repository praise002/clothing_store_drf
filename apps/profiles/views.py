from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from drf_spectacular.utils import extend_schema

from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from apps.common.validators import validate_uuid
from .models import ShippingAddress
from .serializers import (
    ProfileUpdateSerializer,
    ShippingAddressCreateSerializer,
    ShippingAddressSerializer,
    ShippingAddressUpdateSerializer,
)


from .serializers import ProfileSerializer

tags = ["Profiles"]

shipping_tags = ["Shipping Addresses"]


class ShippingAddressListView(APIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List shipping address for the authenticated user",
        description="This endpoint retrieves all shipping addresses for the authenticated user.",
        tags=shipping_tags,
        responses={
            200: ShippingAddressSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        # Retrieve all shipping addresses for the authenticated user
        shipping_addresses = ShippingAddress.objects.filter(user=request.user.profile)

        # Serialize the shipping addresses
        serializer = self.serializer_class(shipping_addresses, many=True)

        return Response(
            {
                "message": "Shipping addresses retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ShippingAddressCreateView(APIView):
    serializer_class = ShippingAddressCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create shipping address",
        description="This endpoint creates an address for shipping orders.",
        tags=shipping_tags,
        responses={
            201: ShippingAddressCreateSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        # Validate the input data
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # Save the shipping address
        shipping_address = serializer.save()

        # Serialize the created shipping address for the response
        shipping_address_serializer = ShippingAddressSerializer(
            shipping_address
        )  # Re-serialize

        return Response(
            {
                "message": "Shipping address created successfully.",
                "data": shipping_address_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class ShippingAddressDetailView(APIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only access their own shipping addresses
        return ShippingAddress.objects.filter(user=self.request.user.profile)

    def get_object(self, pk):
        # Retrieve a specific shipping address for the user
        try:
            return self.get_queryset().get(id=pk)
        except ShippingAddress.DoesNotExist:
            return Response(
                {"error": "Shipping address not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(
        summary="Get a shipping address",
        description="This endpoint retrieves a single shipping address for the authenticated user.",
        tags=shipping_tags,
        responses={
            200: ShippingAddressSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, pk):
        # Retrieve a single shipping address
        shipping_address = self.get_object(pk)

        serializer = self.serializer_class(shipping_address)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a shipping address",
        description="This endpoint updates a shipping address for the authenticated user.",
        tags=shipping_tags,
        responses={
            200: ShippingAddressUpdateSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def patch(self, request, pk):
        # Partially update a shipping address
        shipping_address = self.get_object(pk)

        serializer = ShippingAddressUpdateSerializer(
            shipping_address, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()  # Save the updated instance
        updated_serializer = ShippingAddressSerializer(updated_instance)  # Re-serialize

        return Response(updated_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete a shipping address",
        description="This endpoint deletes a shipping address for the authenticated user.",
        tags=shipping_tags,
        responses={
            204: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, pk):
        # Delete a shipping address
        shipping_address = self.get_object(pk)

        # Allow deletion only if the address is not the default
        if shipping_address.default:
            return Response(
                {"error": "Cannot delete default shipping address."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shipping_address.delete()
        return Response(
            {"message": "Shipping address deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ShippingAddressListGenericView(ListAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve all shipping addresses for the authenticated user.
        """
        # Filter shipping addresses for the authenticated user
        return ShippingAddress.objects.filter(user=self.request.user.profile)

    def list(self, request, *args, **kwargs):
        """
        Override the list method to customize the response format.
        """
        # Get the queryset and serialize it
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # Return the serialized data in the response
        return Response(
            {
                "message": "Shipping addresses retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="List shipping address for the authenticated user",
        description="This endpoint retrieves all shipping addresses for the authenticated user.",
        tags=shipping_tags,
        responses={
            200: ShippingAddressSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """List shipping addresses for the authenticated user."""
        return self.list(request, *args, **kwargs)


class ShippingAddressDetailGenericView(RetrieveUpdateDestroyAPIView):
    queryset = ShippingAddress.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "PUT" or self.request.method == "PATCH":
            return ShippingAddressUpdateSerializer

    def get_queryset(self):
        # Ensure users can only access their own shipping addresses
        return ShippingAddress.objects.filter(user=self.request.user.profile)

    def perform_destroy(self, instance):
        # Allow deletion only if the address is not the default
        if instance.default:
            return Response(
                {"error": "Cannot delete default shipping address."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.delete()

    @extend_schema(
        summary="Get a shipping address",
        description="This endpoint retrieves a single shipping address for the authenticated user.",
        tags=shipping_tags,
        responses={
            200: ShippingAddressSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update a shipping address",
        description="This endpoint updates a shipping address for the authenticated user.",
        tags=shipping_tags,
        responses={
            200: ShippingAddressUpdateSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a shipping address",
        description="This endpoint deletes a shipping address for the authenticated user.",
        tags=shipping_tags,
        responses={
            204: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class MyProfileView(APIView):
    """
    View to retrieve the authenticated user's profile.
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="View a user profile",
        description="This endpoint allows authenticated users to view their profile details. Users can retrieve their account information. Only the account owner can access their profile.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update user profile",
        description="This endpoint allows authenticated users to edit their profile details. Users can update their personal information. Only the account owner can modify their profile.",
        tags=tags,
        responses={
            200: ProfileUpdateSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def patch(self, request):
        profile = request.user.profile
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        profile_serializer = self.serializer_class(profile)  # res-serialize
        return Response(profile_serializer.data, status=status.HTTP_200_OK)


class MyProfileViewGeneric(RetrieveUpdateAPIView):
    """
    View to retrieve and update the authenticated user's profile.
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Return the profile of the authenticated user.
        """
        return self.request.user.profile

    @extend_schema(
        summary="View a user profile",
        description="This endpoint allows authenticated users to view their profile details. Users can retrieve their account information. Only the account owner can access their profile.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve the authenticated user's profile.
        """
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update user profile",
        description="This endpoint allows authenticated users to edit their profile details. Users can update their personal information. Only the account owner can modify their profile.",
        tags=tags,
        responses={
            200: ProfileUpdateSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def patch(self, request, *args, **kwargs):
        """
        Partially update the authenticated user's profile.
        """
        return self.partial_update(request, *args, **kwargs)
