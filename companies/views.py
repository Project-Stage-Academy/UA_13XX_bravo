from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
import logging

from .models import CompanyProfile, UserToCompany, CompanyFollowers, CompanyType, StartupViewHistory
from .serializers import (
    CompanyProfileSerializer,
    UserToCompanySerializer,
    CompanyFollowersSerializer,
    CompanyRegistrationSerializer,
    FollowedStartupSerializer,
    StartupViewHistorySerializer,
)

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




class StartupViewHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list, add and clear the viewing history of startup profiles.
    Only authenticated users with a valid company association can access.
    """
    serializer_class = StartupViewHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Перевірка, чи користувач має доступ до цієї компанії
        company_id = self.request.query_params.get("company_id", None)
        if company_id:
            # Перевіряємо, чи є у користувача компанія
            if not UserToCompany.objects.filter(user=self.request.user, company_id=company_id).exists():
                raise PermissionDenied("You do not have permission to view this company's history.")
        
        # Повертаємо історію переглядів для поточного користувача
        return StartupViewHistory.objects.filter(user=self.request.user).order_by("-viewed_at")

    @action(detail=True, methods=["post"], url_path="view", url_name="mark-viewed")
    def mark_as_viewed(self, request, pk=None):
        """
        Record a view for the specified startup (company) by the authenticated user.
        The user must be associated with the company.
        """
        company_id = pk  # company_id передається як pk
        if not UserToCompany.objects.filter(user=request.user, company_id=company_id).exists():
            raise PermissionDenied("You do not have permission to mark this startup as viewed.")

        try:
            company = CompanyProfile.objects.get(pk=company_id)
        except CompanyProfile.DoesNotExist:
            return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        StartupViewHistory.objects.update_or_create(
            user=request.user,
            company=company,
            defaults={"viewed_at": timezone.now()},
        )

        return Response({"detail": "View recorded successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"], url_path="clear", url_name="clear-history")
    def clear_view_history(self, request):
        """
        Delete all startup view history records for the authenticated user.
        """
        deleted_count, _ = StartupViewHistory.objects.filter(user=request.user).delete()
        return Response(
            {"message": f"Successfully cleared {deleted_count} viewed startup(s)."},
            status=status.HTTP_200_OK
        )