from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "investment_share", "created_at", "updated_at"]
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