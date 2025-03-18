from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CompanyProfile, UserToCompany, CompanyFollowers
from .serializers import CompanyProfileSerializer, UserToCompanySerializer, CompanyFollowersSerializer, CompanyRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
import logging
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
logger = logging.getLogger(__name__)


class CompanyProfileViewSet(viewsets.ModelViewSet):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]

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
    
    def get_investor_company(self, user):
        """Отримує компанію інвестора (enterprise), якщо така існує."""
        try:
            investor_company = user.company_memberships.get(company__type="enterprise")
            return investor_company.company
        except UserToCompany.DoesNotExist:
            return None
        
    def post(self, request, startup_id):
        """Allow an investor to follow a startup."""
        investor = self.get_investor_company(request.user)
        if not investor:
            return Response({"error": "User must be linked to an enterprise company."}, status=status.HTTP_400_BAD_REQUEST)

        startup = get_object_or_404(CompanyProfile, id=startup_id, type="startup")

        if CompanyFollowers.objects.filter(investor=investor, startup=startup).exists():
            return Response({"detail": "You are already following this startup."}, status=status.HTTP_400_BAD_REQUEST)

        follow_relation = CompanyFollowers.objects.create(investor=investor, startup=startup)
        serializer = CompanyFollowersSerializer(follow_relation)

        return Response(serializer.data, status=status.HTTP_201_CREATED)