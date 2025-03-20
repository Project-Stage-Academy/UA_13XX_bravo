from rest_framework import serializers
from .models import CompanyProfile, UserToCompany
from django.db import transaction    


    

class CompanyProfileSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(
        choices=[
            choice[0] for choice in CompanyProfile._meta.get_field("type").choices
        ],
        error_messages={
            "invalid_choice": "Invalid company type. Choose from: {}".format(
                ", ".join(
                    [
                        choice[0]
                        for choice in CompanyProfile._meta.get_field("type").choices
                    ]
                )
            )
        },
    )

    class Meta:
        model = CompanyProfile
        fields = "__all__"

    def validate_company_name(self, value):
        if not value:
            raise serializers.ValidationError("Company name cannot be empty.")
        if CompanyProfile.objects.filter(company_name=value).exists():
            raise serializers.ValidationError(
                "A company with this name already exists."
            )
        return value

    def validate_type(self, value):
        if not value:
            raise serializers.ValidationError("Company type cannot be empty.")
        return value


class UserToCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToCompany
        fields = "__all__"

    def validate_user(self, value):
        if not value:
            raise serializers.ValidationError("User (id) cannot be empty.")
        return value

    def validate_company(self, value):
        if not value:
            raise serializers.ValidationError("Company (id) cannot be empty.")
        return value

    def validate(self, data):
        user = data["user"]
        company = data["company"]

        existing_links = UserToCompany.objects.filter(user=user).values_list(
            "company_id", "company__type"
        )

        if (company.id, company.type) in existing_links:
            raise serializers.ValidationError(
                "This user is already linked to the company."
            )

        if any(company_type == company.type for _, company_type in existing_links):
            raise serializers.ValidationError(
                "This user is already linked to another company with the same type."
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

        with transaction.atomic(): 
            company = CompanyProfile.objects.create(**validated_data)
            UserToCompany.objects.create(user=request.user, company=company)

        return company

