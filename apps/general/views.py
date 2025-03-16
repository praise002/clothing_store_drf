from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.common.responses import CustomResponse
from apps.common.serializers import (
    ErrorDataResponseSerializer,
)

from .models import SiteDetail, TeamMember
from .serializers import (
    MessageResponseSerializer,
    SiteDetailResponseSerializer,
    SiteDetailSerializer,
    TeamMemberResponseSerializer,
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
            200: SiteDetailResponseSerializer,
        },
        auth=[],
    )
    def get(self, request):
        """Retrieve the single SiteDetail object."""
        site_detail, _ = SiteDetail.objects.get_or_create()
        serializer = self.serializer_class(site_detail)
        return CustomResponse.success(
            message="Site detail retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class TeamMemberListView(APIView):
    serializer_class = TeamMemberSerializer

    @extend_schema(
        summary="List all TeamMember objects",
        description="This endpoint lists all TeamMember objects",
        tags=tags,
        responses={
            200: TeamMemberResponseSerializer,
        },
        auth=[],
    )
    def get(self, request):
        """List all TeamMember objects."""
        team_members = TeamMember.objects.all()
        serializer = self.serializer_class(team_members, many=True)
        return CustomResponse.success(
            message="TeamMembers retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class MessageCreateView(APIView):
    serializer_class = MessageSerializer

    @extend_schema(
        summary="Create a new Message object",
        description="This endpoint creates a new Message object",
        tags=tags,
        responses={
            201: MessageResponseSerializer,
            400: ErrorDataResponseSerializer,
        },
        auth=[],
    )
    def post(self, request):
        """Create a new Message object."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return CustomResponse.success(
            message="Message sent successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )
