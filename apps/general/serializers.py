from rest_framework import serializers

from apps.common.serializers import BaseModelSerializer
from .models import Social, SiteDetail, TeamMember, Message

class SocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Social
        fields = ['id', 'fb', 'tw', 'ln', 'ig', 'name']

class SiteDetailSerializer(BaseModelSerializer):
    company_socials = SocialSerializer(read_only=True)

    class Meta:
        model = SiteDetail
        fields = [
            'name',
            'description',
            'phone',
            'address',
            'email',
            'company_socials',
        ]

class TeamMemberSerializer(BaseModelSerializer):
    social_links = SocialSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    # avatar_url = serializers.ReadOnlyField(source='avatar_url') # OR THIs

    class Meta:
        model = TeamMember
        fields = [
            'name',
            'role',
            'description',
            'avatar_url',
            'social_links',
        ]

    def get_avatar_url(self, obj):
        return obj.avatar_url

class MessageSerializer(BaseModelSerializer):
    class Meta:
        model = Message
        fields = [
            'name',
            'email',
            'subject',
            'text',
            'sent_at',
        ]