from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.common.serializers import (
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from .models import SiteDetail, TeamMember
from .serializers import (
    SiteDetailSerializer,
    TeamMemberSerializer,
    MessageSerializer,
)


tags = ["General"]


class SiteDetailView(APIView):
    serializer_class = SiteDetailSerializer

    @extend_schema(
        summary="Retrieve the single SiteDetail object",
        description="This endpoint retrieves the single SiteDetail object",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
        },
        auth=[],
    )
    def get(self, request):
        """Retrieve the single SiteDetail object."""
        site_detail, _ = SiteDetail.objects.get_or_create()
        serializer = self.serializer_class(site_detail)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamMemberListView(APIView):
    serializer_class = TeamMemberSerializer

    @extend_schema(
        summary="List all TeamMember objects",
        description="This endpoint lists all TeamMember objects",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,
        },
        auth=[],
    )
    def get(self, request):
        """List all TeamMember objects."""
        team_members = TeamMember.objects.all()
        serializer = self.serializer_class(team_members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageCreateView(APIView):
    serializer_class = MessageSerializer

    @extend_schema(
        summary="Create a new Message object",
        description="This endpoint creates a new Message object",
        tags=tags,
        responses={
            201: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
        },
        auth=[],
    )
    def post(self, request):
        """Create a new Message object."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = {
            "message": "Message sent successfully.",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
