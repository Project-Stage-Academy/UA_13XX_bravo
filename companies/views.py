from rest_framework import viewsets
from .models import CompanyProfile, UserToCompany
from .serializers import CompanyProfileSerializer, UserToCompanySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError


class CompanyProfileViewSet(viewsets.ModelViewSet):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """When creating a company, it automatically adds a user connection."""
        company = serializer.save()

        data = {
            "user": self.request.user.id,
            "company": company.id,
        }
        user_to_company_serializer = UserToCompanySerializer(data=data)

        if user_to_company_serializer.is_valid():
            user_to_company_serializer.save()
        else:
            raise ValidationError(user_to_company_serializer.errors)


class UserToCompanyViewSet(viewsets.ModelViewSet):
    queryset = UserToCompany.objects.all()
    serializer_class = UserToCompanySerializer
    permission_classes = [IsAuthenticated]
