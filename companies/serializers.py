from rest_framework import serializers
from .models import CompanyProfile, UserToCompany



class CompanyProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the CompanyProfile model.

    This serializer handles the validation and serialization of CompanyProfile instances.
    """
    class Meta:
        """
        Meta class to map serializer's fields with the model fields.
        """
        model = CompanyProfile
        fields = "__all__"

    def validate_company_name(self, value):
        """
        Validate that the company name is not empty and unique.

        Args:
            value (str): The company name to validate.

        Raises:
            serializers.ValidationError: If the company name is empty or already exists.

        Returns:
            str: The validated company name.
        """
        if not value:
            raise serializers.ValidationError("Company name cannot be empty.")
        if CompanyProfile.objects.filter(company_name=value).exists():
            raise serializers.ValidationError(
                "A company with this name already exists."
            )
        return value

    def validate_type(self, value):
        """
        Validate that the company type is not empty.

        Args:
            value (str): The company type to validate.

        Raises:
            serializers.ValidationError: If the company type is empty.

        Returns:
            str: The validated company type.
        """
        if not value:
            raise serializers.ValidationError("Company type cannot be empty.")
        return value


class UserToCompanySerializer(serializers.ModelSerializer):
    """
    Serializer for the UserToCompany model.

    This serializer handles the validation and serialization of UserToCompany instances.
    """
    class Meta:
        """
        Meta class to map serializer's fields with the model fields.
        """
        model = UserToCompany
        fields = "__all__"

    def validate_user(self, value) -> int:
        """
        Validate that the user ID is not empty.

        Args:
            value (int): The user ID to validate.

        Raises:
            serializers.ValidationError: If the user ID is empty.

        Returns:
            int: The validated user ID.
        """
        if not value:
            raise serializers.ValidationError("User (id) cannot be empty.")
        return value

    def validate_company(self, value) -> int:
        """
        Validate that the company ID is not empty.

        Args:
            value (int): The company ID to validate.

        Raises:
            serializers.ValidationError: If the company ID is empty.

        Returns:
            int: The validated company ID.
        """
        if not value:
            raise serializers.ValidationError("Company (id) cannot be empty.")
        return value

    def validate(self, data: dict) -> dict:
        """
        Validate that the user is not already linked to the company.

        Args:
            data (dict): The data to validate.

        Raises:
            serializers.ValidationError: If the user is already linked to the company.

        Returns:
            dict: The validated data.
        """
        if UserToCompany.objects.filter(
            user=data["user"], company=data["company"]
        ).exists():
            raise serializers.ValidationError(
                "This user is already linked to the company."
            )
        return data
    





class CompanyRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new company.

    This serializer handles the creation of a new company and associates it with the authenticated user.
    """
    class Meta:
        """
        Meta class to map serializer's fields with the model fields.
        """
        model = CompanyProfile
        fields = ["company_name", "description", "type"]

    def create(self, validated_data: dict) -> CompanyProfile:
        """
        Create a new company and associate it with the authenticated user.

        Args:
            validated_data (dict): The data to create a new company with.

        Raises:
            serializers.ValidationError: If the user is not authenticated.

        Returns:
            CompanyProfile: The created company instance.
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("User must be authenticated to create a company.")

        company = CompanyProfile.objects.create(**validated_data)
        UserToCompany.objects.create(user=request.user, company=company)
        return company

