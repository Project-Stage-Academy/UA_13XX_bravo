from rest_framework import serializers
from .models import Notification, NotificationPreference, Type, User, Entity


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )
    content = serializers.CharField(max_length=500, required=True)
    read = serializers.BooleanField(default=False)
    entity = EntitySerializer(required=False, allow_null=True)
    type = serializers.CharField()

    class Meta:
        model = Notification
        fields = fields = [
            "id",
            "user",
            "entity",
            "type",
            "content",
            "created_at",
            "read",
        ]

    def validate(self, data):
        request = self.context.get("request")
        if request and request.method != "PATCH":
            if (
                data.get("user", None) is None
                or data.get("type", None) is None
                or data.get("content", None) is None
            ):
                raise serializers.ValidationError(
                    "User, type, and content are required fields."
                )

        return data

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
        return type_obj

    def create(self, validated_data):
        entity_data = validated_data.pop("entity", None)

        entity = None
        if entity_data:
            entity, _ = Entity.objects.get_or_create(**entity_data)

        notification = Notification.objects.create(entity=entity, **validated_data)
        return notification

    def update(self, instance, validated_data):
        entity_data = validated_data.pop("entity", None)

        if entity_data:
            entity, _ = Entity.objects.get_or_create(**entity_data)
            instance.entity = entity

        instance.content = validated_data.get("content", instance.content)
        instance.read = validated_data.get("read", instance.read)

        type_obj = validated_data.get("type", instance.type)
        if isinstance(type_obj, Type):
            instance.type = type_obj
        elif isinstance(type_obj, str):
            instance.type = Type.objects.get(name=type_obj)

        instance.save()
        return instance


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    enabled = serializers.BooleanField(default=True)
    type = serializers.CharField()  # Using CharField instead of SlugRelatedField
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )

    class Meta:
        model = NotificationPreference
        fields = ["user", "type", "enabled"]
        read_only_fields = ["user"]

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
