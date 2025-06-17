from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.views import APIView

from apps.common.responses import CustomResponse
from apps.general.schema_examples import (
    MESSAGE_RESPONSE_EXAMPLE,
    SITE_DETAIL_RESPONSE_EXAMPLE,
    TEAM_MEMBER_RESPONSE_EXAMPLE,
)

from .models import SiteDetail, TeamMember
from .serializers import MessageSerializer, SiteDetailSerializer, TeamMemberSerializer

tags = ["General"]


class SiteDetailView(APIView):
    serializer_class = SiteDetailSerializer

    @extend_schema(
        summary="Retrieve the single SiteDetail object",
        description="This endpoint retrieves the single SiteDetail object",
        tags=tags,
        responses=SITE_DETAIL_RESPONSE_EXAMPLE,
        auth=[],
    )
    def get(self, request):
        """Retrieve the single SiteDetail object."""
        site_detail, _ = SiteDetail.objects.get_or_create()
        serializer = self.serializer_class(site_detail)
        return CustomResponse.success(
            message="Site detail retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class TeamMemberListView(APIView):
    serializer_class = TeamMemberSerializer

    @extend_schema(
        summary="List all TeamMember objects",
        description="This endpoint lists all TeamMember objects",
        tags=tags,
        responses=TEAM_MEMBER_RESPONSE_EXAMPLE,
        auth=[],
    )
    def get(self, request):
        """List all TeamMember objects."""
        team_members = TeamMember.objects.select_related('social_links').all()
        serializer = self.serializer_class(team_members, many=True)
        return CustomResponse.success(
            message="Team members retrieved successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )


class MessageCreateView(APIView):
    serializer_class = MessageSerializer

    @extend_schema(
        summary="Create a new Message object",
        description="This endpoint creates a new Message object",
        tags=tags,
        responses=MESSAGE_RESPONSE_EXAMPLE,
        auth=[],
    )
    def post(self, request):
        """Create a new Message object."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return CustomResponse.success(
            message="Message sent successfully.",
            status_code=status.HTTP_201_CREATED,
        )
