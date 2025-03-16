from rest_framework import serializers

from apps.common.serializers import SuccessResponseSerializer

from .models import Social, SiteDetail, TeamMember, Message


class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = ["id", "fb", "tw", "ln", "ig", "name"]


class SiteDetailSerializer(serializers.ModelSerializer):
    company_socials = SocialSerializer(read_only=True)

    class Meta:
        model = SiteDetail
        fields = [
            "name",
            "description",
            "phone",
            "address",
            "email",
            "company_socials",
        ]


class TeamMemberSerializer(serializers.ModelSerializer):
    social_links = SocialSerializer(read_only=True)

    class Meta:
        model = TeamMember
        fields = [
            "name",
            "role",
            "description",
            "avatar_url",
            "social_links",
        ]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "name",
            "email",
            "subject",
            "text",
            "sent_at",
        ]

# Responses
class SiteDetailResponseSerializer(SuccessResponseSerializer):
    data = SiteDetailSerializer()
    
class TeamMemberResponseSerializer(SuccessResponseSerializer):
    data = TeamMemberSerializer()
    
class MessageResponseSerializer(SuccessResponseSerializer):
    data = MessageSerializer()