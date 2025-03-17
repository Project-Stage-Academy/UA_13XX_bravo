from rest_framework import serializers
from .models import Notification, NotificationPreference, Type


class NotificationSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=500, required=True)
    read = serializers.BooleanField(default=False)

    class Meta:
        model = Notification
        fields = "__all__"

    def validate_content(self, value):
        if value is None or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value

    def validate(self, data):
        existing_query = Notification.objects.filter(
            user=data["user"], type=data["type"], entity=data.get("entity", None)
        )

        if self.instance:
            existing_query = existing_query.exclude(id=self.instance.id)

        if existing_query.exists():
            raise serializers.ValidationError(
                "A notification with this user, type, and entity already exists."
            )

        return data


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    enabled = serializers.BooleanField(default=True)
    type = serializers.CharField()

    class Meta:
        model = NotificationPreference
        fields = ["type", "enabled"]

    def create(self, validated_data):
        type_name = validated_data.pop("type")
        type_obj = Type.objects.filter(name=type_name).first()

        if not type_obj:
            raise serializers.ValidationError({"type": "Invalid type name"})

        return NotificationPreference.objects.create(type=type_obj, **validated_data)
