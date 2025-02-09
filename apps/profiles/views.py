from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from drf_spectacular.utils import extend_schema

from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)

from .serializers import ProfileSerializer

tags = ["Profiles"]


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
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def patch(self, request):
        profile = request.user.profile
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def patch(self, request, *args, **kwargs):
        """
        Partially update the authenticated user's profile.
        """
        return self.partial_update(request, *args, **kwargs)
