from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from .models import CompanyProfile, UserToCompany, CompanyFollowers, CompanyType
from .serializers import CompanyProfileSerializer, UserToCompanySerializer, CompanyFollowersSerializer, CompanyRegistrationSerializer
import logging

from django.db import transaction
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.utils import IntegrityError
from .models import CompanyProfile, UserToCompany, CompanyFollowers, CompanyType
from .serializers import (
    CompanyProfileSerializer,
    UserToCompanySerializer,
    CompanyFollowersSerializer,
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


class FollowStartupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, startup_id):
        """Allow an investor to follow a startup."""
        try:
            investor_company = request.user.company_memberships.get(company__type=CompanyType.ENTERPRISE).company
        except UserToCompany.DoesNotExist:
            if not request.user.company_memberships.exists():
                return Response({"error": "User is not associated with any company."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "User is not linked to an enterprise company."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            startup = get_object_or_404(CompanyProfile, id=startup_id, type=CompanyType.STARTUP)
        except Http404:
            return Response({"error": "Startup not found."} ,status=status.HTTP_404_NOT_FOUND)
        if CompanyFollowers.objects.filter(investor=investor_company, startup=startup).exists():
            return Response({"detail": "You are already following this startup."}, status=status.HTTP_400_BAD_REQUEST)

        follow_relation = CompanyFollowers.objects.create(investor=investor_company, startup=startup)
        serializer = CompanyFollowersSerializer(follow_relation)

        return Response(serializer.data, status=status.HTTP_201_CREATED)