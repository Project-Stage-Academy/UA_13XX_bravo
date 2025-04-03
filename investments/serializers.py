from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subscription model. 
    Handles creation and validation of investment shares.
    """
    class Meta:
        model = Subscription
        fields = ["investment_share", "project"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_investment_share(self, value):
        if value <= 0:
            raise serializers.ValidationError("Investment share must be greater than 0.")
        if value > 100:
            raise serializers.ValidationError("Investment share cannot exceed 100.")
        return value

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)