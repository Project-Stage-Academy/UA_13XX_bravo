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

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", "")
        )
        user.set_password(validated_data["password"])  
        user.save()
        return user
     
    
    
    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            validate_password(password)  
            instance.set_password(password)  

        return super().update(instance, validated_data)
    


