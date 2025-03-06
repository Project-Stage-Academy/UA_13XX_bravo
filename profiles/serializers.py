from rest_framework import serializers
from .models import CompanyProfile, UserToCompany


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = "__all__"

    def validate_company_name(self, value):
        if not value:
            raise serializers.ValidationError("Company name cannot be empty.")
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
