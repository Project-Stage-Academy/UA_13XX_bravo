from rest_framework import serializers
from users.models import User
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    phone = PhoneNumberField()


    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'phone']
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        try:
            validate_email(value) 
        except ValidationError:
            raise serializers.ValidationError("Invalid email format.")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)  
        return value


     
    
    
    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            validate_password(password)  
            instance.set_password(password)  

        return super().update(instance, validated_data)
    

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    re_password = serializers.CharField(write_only=True, required=True)
    phone = PhoneNumberField()

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 're_password', 'first_name', 'last_name', 'phone']

    def validate(self, data):
        if data["password"] != data["re_password"]:
            raise serializers.ValidationError({"re_password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("re_password")
        user = User.objects.create_user(**validated_data)
        return user

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )

    def validate_new_password(self, value):
        validate_password(value)
        return value


