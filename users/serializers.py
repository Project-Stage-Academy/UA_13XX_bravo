from rest_framework import serializers
from users.models import User
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from companies.models import UserToCompany

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, handling user data including password validation and update operations.

    Attributes:
        password (CharField): A write-only field for the user's password, with a minimum length of 8 characters.
        phone (PhoneNumberField): A field for the user's phone number.
    """
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    phone = PhoneNumberField()

    class Meta:
        """
        Meta class to map serializer's fields with the model fields.
        """
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'phone']
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, value: str) -> str:
        """
        Validate the email format and ensure it is unique.

        Args:
            value (str): The email address to validate.

        Raises:
            ValidationError: If the email format is invalid or already exists in the database.

        Returns:
            str: The validated email address.
        """
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format.")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value: str) -> str:
        """
        Validate the password using Django's password validators.

        Args:
            value (str): The password to validate.

        Returns:
            str: The validated password.
        """
        validate_password(value)
        return value

    def update(self, instance: User, validated_data: dict) -> User:
        """
        Update a user instance with validated data.

        Args:
            instance (User): The user instance to update.
            validated_data (dict): The data to update the user instance with.

        Returns:
            User: The updated user instance.
        """
        if "password" in validated_data:
            password = validated_data.pop("password")
            validate_password(password)
            instance.set_password(password)

        return super().update(instance, validated_data)

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user, ensuring password confirmation and handling user creation.

    Attributes:
        password (CharField): A write-only field for the user's password, with a minimum length of 8 characters.
        re_password (CharField): A write-only field for confirming the user's password.
        phone (PhoneNumberField): A field for the user's phone number.
    """
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    re_password = serializers.CharField(write_only=True, required=True)
    phone = PhoneNumberField()

    class Meta:
        """
        Meta class to map serializer's fields with the model fields.
        """
        model = User
        fields = ['id', 'email', 'password', 're_password', 'first_name', 'last_name', 'phone']

    def validate(self, data: dict) -> dict:
        """
        Validate that the password and confirmed password match.

        Args:
            data (dict): The data to validate.

        Raises:
            ValidationError: If the passwords do not match.

        Returns:
            dict: The validated data.
        """
        if data["password"] != data["re_password"]:
            raise serializers.ValidationError({"re_password": "Passwords do not match"})
        return data

    def create(self, validated_data: dict) -> User:
        """
        Create a new user with the validated data.

        Args:
            validated_data (dict): The data to create a new user with.

        Returns:
            User: The created user instance.
        """
        validated_data.pop("re_password")
        user = User.objects.create_user(**validated_data)
        return user


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for handling password reset requests and confirmations.
    
    It supports two modes:
    1. Requesting a password reset via email.
    2. Confirming the password reset with a new password.
    """
    email = serializers.EmailField(required=False)
    new_password = serializers.CharField(write_only=True, min_length=8, required=False, style = { "input_type" : "password" }, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, min_length=8, required=False, style = { "input_type" : "password" })

    def validate(self, data):
        if "new_password" in data and "confirm_password" in data:
            if data['new_password'] != data['confirm_password']:
                raise serializers.ValidationError({"new_password": ["Passwords do not match."]})
            
            try:
                validate_password(data["new_password"])
            except serializers.ValidationError as e:
                raise serializers.ValidationError({"new_password": e.messages})
            
        elif "email" not in data:
            raise serializers.ValidationError("Either email or new password must be provided.")
        
        return data

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            return value
        return value


class LoginSerializer(serializers.Serializer):
    """
    Serializer for handling user login, validating email and password.

    Attributes:
        email (EmailField): A field for the user's email address.
        password (CharField): A write-only field for the user's password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    company_id = serializers.IntegerField(required=False)

    def validate(self, attrs: dict) -> dict:
        """
        Validate and add company_id to the token payload if provided.

        Args:
            attrs (dict): The attributes to validate.

        Raises:
            ValidationError: If company_id is provided but user is not associated with the company.

        Returns:
            dict: The validated data with company_id.
        """
        data = super().validate(attrs)
        company_id = attrs.get("company_id")

        if company_id:
            user = self.user
            if not UserToCompany.objects.filter(user=user, company_id=company_id).exists():
                raise serializers.ValidationError("User is not associated with this company.")
            data["company_id"] = company_id

        return data

    @classmethod
    def get_token(cls, user: User) -> dict:
        """
        Customize the token payload to include company_id if provided.

        Args:
            user (User): The user for whom the token is generated.

        Returns:
            dict: The token payload with company_id if provided.
        """
        token = super().get_token(user)
        token["email"] = user.email

        company_id = cls.context["request"].data.get("company_id")
        if company_id:
            token["company_id"] = company_id

        return token

