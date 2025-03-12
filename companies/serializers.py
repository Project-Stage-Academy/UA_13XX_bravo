from rest_framework import serializers
from .models import CompanyProfile, UserToCompany, COMPANY_TYPES


class CompanyProfileSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(
        choices=list(dict(COMPANY_TYPES).keys()),
        error_messages={
            "invalid_choice": "Invalid company type. Choose from: {}".format(
                ", ".join(dict(COMPANY_TYPES).keys())
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

        if UserToCompany.objects.filter(user=user, company=company).exists():
            raise serializers.ValidationError(
                "This user is already linked to the company."
            )

        company_type = company.type

        if UserToCompany.objects.filter(user=user, company__type=company_type).exists():
            raise serializers.ValidationError(
                "This user is already linked to another company with the same type."
            )

        return data
