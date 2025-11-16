from rest_framework import serializers
from apps.orders.models import TrackingNumber

class TrackingNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingNumber
        fields = ["number"]