from rest_framework import serializers
from .models import Notification, NotificationPreference, Type, User, Entity


class NotificationSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=500, required=True)
    read = serializers.BooleanField(default=False)
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Notification
        fields = "__all__"

    def validate_content(self, value):
        if value is None or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value

    def validate(self, data):
        entity = data.get("entity", None)

        existing_query = Notification.objects.filter(
            user=data["user"], type=data["type"], entity=entity
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
    type = serializers.CharField()  # Using CharField instead of SlugRelatedField

    class Meta:
        model = NotificationPreference
        fields = ["user", "type", "enabled"]
        read_only_fields = ["user"]
        user = serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all(), required=False
        )

    def validate_type(self, value):
        """Validate if the provided type name exists in the database."""
        type_obj = Type.objects.filter(name=value).first()
        if not type_obj:
            raise serializers.ValidationError(
                {
                    "type": f"Type '{value}' does not exist.",
                    "available_types": list(
                        Type.objects.values_list("name", flat=True)
                    ),
                }
            )
        return type_obj  # Returning the object instead of a string

    def validate(self, data):
        """Ensure that the user does not have duplicate notification preferences."""
        type_obj = data.get("type")  # validate_type() already returns a Type object

        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            data["user"] = request.user
        else:
            raise serializers.ValidationError({"user": "Authentication required."})

        if NotificationPreference.objects.filter(
            user=data["user"], type=type_obj
        ).exists():
            raise serializers.ValidationError(
                "A preference with this user and type already exists."
            )

        data["type"] = type_obj  # Replacing the string with the Type object
        return data

    def create(self, validated_data):
        """Create a new NotificationPreference instance."""
        return NotificationPreference.objects.create(**validated_data)


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ["id", "name"]
