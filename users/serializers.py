from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer handles the creation of a new user, ensuring the password is
    write-only and meets the minimum length requirement.
    """

    password = serializers.CharField(write_only=True, min_length=8, required=True)

    class Meta:
        """
        Meta class to map serializer's fields with the model fields.
        """
        model = User
        fields = ["id", "email", "password"]

    def create(self, validated_data):
        """
        Create a new user with the provided validated data.

        Args:
            validated_data (dict): Validated data containing user details.

        Returns:
            User: The created user instance.
        """
        user = User(
            email=validated_data["email"],
            is_active=False,  
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
