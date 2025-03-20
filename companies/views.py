import logging

from django.db import transaction
from rest_framework import viewsets, filters
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import CompanyProfile, UserToCompany
from .serializers import (
    CompanyProfileSerializer,
    UserToCompanySerializer,
    CompanyRegistrationSerializer,
)




logger = logging.getLogger(__name__)

class CompanyProfileViewSet(viewsets.ModelViewSet):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["company_name", "description"]
    filterset_fields = ["type", "industry", "required_funding", "company_size"]
    ordering_fields = ["company_size", "required_funding", "created_at", "updated_at"]

    def perform_create(self, serializer):
        """When creating a company, it automatically adds a user connection."""
        with transaction.atomic():  # Ensures both operations succeed or fail together
            company = serializer.save()

            user_to_company_serializer = UserToCompanySerializer(
                data={"user": self.request.user.id, "company": company.id}
            )

            if user_to_company_serializer.is_valid():
                user_to_company_serializer.save()
            else:
                raise ValidationError(user_to_company_serializer.errors)


class UserToCompanyViewSet(viewsets.ModelViewSet):
    queryset = UserToCompany.objects.all()
    serializer_class = UserToCompanySerializer
    permission_classes = [IsAuthenticated]



class RegisterCompanyView(CreateAPIView):
    """
    A view for registering a new company.

    This view handles the creation of a new company and associates it with the authenticated user.
    """
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Create a new company and associate it with the authenticated user.

        Args:
            serializer: The serializer instance containing the company data.

        Raises:
            Exception: If an error occurs during the company registration process.

        Returns:
            None
        """
        try:
            company = serializer.save()
            if not UserToCompany.objects.filter(user=self.request.user, company=company).exists():
                UserToCompany.objects.create(user=self.request.user, company=company)
            else:
                logger.warning(f"User {self.request.user} is already associated with company {company}.")
        except Exception as e:
            logger.error(f"Error registering company: {e}")
            raise

