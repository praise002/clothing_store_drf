from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import NotFoundError
from apps.common.responses import CustomResponse
from apps.profiles.schema_examples import (
    AVATAR_UPDATE_RESPONSE_EXAMPLE,
    PROFILE_RETRIEVE_RESPONSE_EXAMPLE,
    PROFILE_UPDATE_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESS_CREATE_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESS_DETAIL_DELETE_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESS_DETAIL_GET_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESS_DETAIL_PATCH_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESS_RETRIEVE_RESPONSE_EXAMPLE,
    build_avatar_request_schema,
)

from .models import ShippingAddress
from .serializers import (
    AvatarSerializer,
    ProfileSerializer,
    ShippingAddressCreateSerializer,
    ShippingAddressSerializer,
    ShippingAddressUpdateSerializer,
)

tags = ["Profiles"]

shipping_tags = ["Shipping Addresses"]


class ShippingAddressListView(APIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List shipping address for the authenticated user",
        description="This endpoint retrieves all shipping addresses for the authenticated user.",
        tags=shipping_tags,
        responses=SHIPPING_ADDRESS_RETRIEVE_RESPONSE_EXAMPLE,
    )
    def get(self, request):
        # Retrieve all shipping addresses for the authenticated user
        shipping_addresses = ShippingAddress.objects.filter(user=request.user.profile)

        # Serialize the shipping addresses
        serializer = self.serializer_class(shipping_addresses, many=True)

        return CustomResponse.success(
            message="Shipping addresses retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class ShippingAddressCreateView(APIView):
    serializer_class = ShippingAddressCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create shipping address",
        description="""
            This endpoint creates an address for shipping orders.
            
            Important Notes:
            - The `state` field must be one of the 36 states in Nigeria. 
            - Valid state names are case-sensitive and include:
            Abia, Adamawa, Akwa Ibom, Anambra, Bauchi, Bayelsa, Benue, Borno, Cross River,
            Delta, Ebonyi, Edo, Ekiti, Enugu, Gombe, Imo, Jigawa, Kaduna, Kano, Katsina,
            Kebbi, Kogi, Kwara, Lagos, Nasarawa, Niger, Ogun, Ondo, Osun, Oyo, Plateau,
            Rivers, Sokoto, Taraba, Yobe, Zamfara.
            """,
        tags=shipping_tags,
        responses=SHIPPING_ADDRESS_CREATE_RESPONSE_EXAMPLE,
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

        return CustomResponse.success(
            message="Shipping address created successfully.",
            data=shipping_address_serializer.data,
            status_code=status.HTTP_201_CREATED,
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
            raise NotFoundError(
                err_msg="Shipping address not found.",
            )
            # from rest_framework.exceptions import NotFound
            # raise NotFound()

    @extend_schema(
        summary="Get a shipping address",
        description="This endpoint retrieves a single shipping address for the authenticated user.",
        tags=shipping_tags,
        responses=SHIPPING_ADDRESS_DETAIL_GET_RESPONSE_EXAMPLE,
    )
    def get(self, request, pk):
        # Retrieve a single shipping address
        shipping_address = self.get_object(pk)

        serializer = self.serializer_class(shipping_address)
        return CustomResponse.success(
            message="Shipping address retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update a shipping address",
        description="This endpoint updates a shipping address for the authenticated user.",
        tags=shipping_tags,
        responses=SHIPPING_ADDRESS_DETAIL_PATCH_RESPONSE_EXAMPLE,
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

        return CustomResponse.success(
            message="Shipping address updated successfully.",
            data=updated_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a shipping address",
        description="This endpoint deletes a shipping address for the authenticated user.",
        tags=shipping_tags,
        responses=SHIPPING_ADDRESS_DETAIL_DELETE_RESPONSE_EXAMPLE,
    )
    def delete(self, request, pk):
        # Delete a shipping address
        shipping_address = self.get_object(pk)

        # Allow deletion only if the address is not the default
        try:
            shipping_address.delete()
        except ValueError as e:
            raise PermissionDenied(detail=str(e))

        return Response(status=status.HTTP_204_NO_CONTENT)


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
        return CustomResponse.success(
            message="Shipping addresses retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="List shipping address for the authenticated user",
        description="This endpoint retrieves all shipping addresses for the authenticated user.",
        tags=shipping_tags,
        responses=SHIPPING_ADDRESS_RETRIEVE_RESPONSE_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        """List shipping addresses for the authenticated user."""
        return self.list(request, *args, **kwargs)


class ShippingAddressDetailGenericView(RetrieveUpdateDestroyAPIView):
    queryset = ShippingAddress.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "get",
        "patch",
        "delete",
        "head",
        "options",
    ]  # to remove the put method inherited from RetrieveUpdateDestroy

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ShippingAddressUpdateSerializer
        return ShippingAddressSerializer

    def get_queryset(self):
        # Ensure users can only access their own shipping addresses
        return ShippingAddress.objects.filter(user=self.request.user.profile)

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ValueError as e:
            raise PermissionDenied(detail=str(e))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.success(
            message="Shipping address deleted successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )

    @extend_schema(
        summary="Get a shipping address",
        description="This endpoint retrieves a single shipping address for the authenticated user.",
        tags=shipping_tags,
        responses=SHIPPING_ADDRESS_DETAIL_GET_RESPONSE_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        """
        Retrieve object and handle custom 404 response
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Get lookup field and value
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        try:
            # {'pk': UUID('5fe1da59-52cd-4f69-802d-b59acb757f21')} - returns this without unpacking
            # Becomes:
            # queryset.get(pk=UUID('5fe1da59-52cd-4f69-802d-b59acb757f21'))
            obj = queryset.get(**{self.lookup_field: lookup_value})
        except ShippingAddress.DoesNotExist:
            raise NotFoundError(
                err_msg="Shipping address not found.",
            )

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(
            message="Shipping address retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update a shipping address",
        description="This endpoint updates a shipping address for the authenticated user.",
        tags=shipping_tags,
        responses=SHIPPING_ADDRESS_DETAIL_PATCH_RESPONSE_EXAMPLE,
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        updated_instance = serializer.instance
        updated_serializer = ShippingAddressSerializer(updated_instance)
        return CustomResponse.success(
            message="Shipping address updated successfully.",
            data=updated_serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Delete a shipping address",
        description="This endpoint deletes a shipping address for the authenticated user.",
        tags=shipping_tags,
        responses=SHIPPING_ADDRESS_DETAIL_DELETE_RESPONSE_EXAMPLE,
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
        responses=PROFILE_RETRIEVE_RESPONSE_EXAMPLE,
    )
    def get(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile)
        return CustomResponse.success(
            message="Profile retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update user profile",
        description="This endpoint allows authenticated users to edit their profile details. Users can update their personal information. Only the account owner can modify their profile.",
        tags=tags,
        responses=PROFILE_UPDATE_RESPONSE_EXAMPLE,
    )
    def patch(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        return CustomResponse.success(
            message="Profile updated successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class MyProfileViewGeneric(RetrieveUpdateAPIView):
    """
    View to retrieve and update the authenticated user's profile.
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "get",
        "patch",
        "head",
        "options",
    ]  # to remove the put method inherited from RetrieveUpdate

    def get_object(self):
        """
        Return the profile of the authenticated user.
        """
        return self.request.user.profile

    @extend_schema(
        summary="View a user profile",
        description="This endpoint allows authenticated users to view their profile details. Users can retrieve their account information. Only the account owner can access their profile.",
        tags=tags,
        responses=PROFILE_RETRIEVE_RESPONSE_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve the authenticated user's profile.
        """
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(
            message="Profile retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update user profile",
        description="This endpoint allows authenticated users to edit their profile details. Users can update their personal information. Only the account owner can modify their profile.",
        tags=tags,
        responses=PROFILE_UPDATE_RESPONSE_EXAMPLE,
    )
    def patch(self, request, *args, **kwargs):
        """
        Partially update the authenticated user's profile.
        """
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Override the update method to customize the response format.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return CustomResponse.success(
            message="Profile updated successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class AvatarUpdateView(APIView):
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update user avatar",
        description="This endpoint allows authenticated users to upload or update their profile avatar.",
        tags=tags,
        request=build_avatar_request_schema(),
        responses=AVATAR_UPDATE_RESPONSE_EXAMPLE,
    )
    def patch(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        

        return CustomResponse.success(
            message="Profile avatar updated successfully.",
            data={
                "avatar_url": profile.avatar_url,
            },
            status_code=status.HTTP_200_OK,
        )
