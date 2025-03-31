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
from users.models import UserRole
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes

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



def record_view(user, company):
    """
    Record the view of a startup by a user, or update the viewed_at timestamp if the user has already viewed the startup.
    """
    if user.is_authenticated:
        StartupViewHistory.objects.update_or_create(
            user=user,
            company=company,
            defaults={"viewed_at": timezone.now()}
        )

class StartupViewHistoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint to list, add and clear the viewing history of startup profiles.
    Only authenticated users with a valid company association can access.
    """
    queryset = StartupViewHistory.objects.all()
    serializer_class = StartupViewHistorySerializer
    permission_classes = [IsAuthenticated]

    def _check_permissions(self, user, company_id=None):
        """
        Helper method to check permissions for the current user.
        """
        if company_id and not UserToCompany.objects.filter(user=user, company_id=company_id).exists():
            raise PermissionDenied("You do not have permission to access this company's history.")
        if user.role.name != UserRole.INVESTOR:
            raise PermissionDenied("Only investors can perform this action.")

    @extend_schema(
        description="Get the view history of a startup for the authenticated user.",
        parameters=[
            OpenApiParameter(
                name='company_id',
                type=int,
                location=OpenApiParameter.QUERY,
                description="Company ID to filter history"
            )
        ],
        responses={200: StartupViewHistorySerializer(many=True)}
    )
    def get_queryset(self):
        return StartupViewHistory.objects.all()

    @extend_schema(
        description="Retrieve the details of a startup profile and record the view for the authenticated user.",
        responses={200: StartupViewHistorySerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        record_view(request.user, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        description="Clear all viewed history for the authenticated user.",
        responses={200: OpenApiTypes.OBJECT}
    )
    @action(detail=False, methods=["delete"], url_path="clear", url_name="clear-history")
    def clear_view_history(self, request):
        company_id = request.query_params.get("company_id", None)

        if company_id:
            self._check_permissions(request.user, company_id)
            queryset = StartupViewHistory.objects.filter(user=request.user, company_id=company_id)
        else:
            self._check_permissions(request.user)
            queryset = StartupViewHistory.objects.filter(user=request.user)

        deleted_count, _ = queryset.delete()
        
        if deleted_count == 0:
            return Response({"message": "No viewed startups to clear."}, status=status.HTTP_200_OK)

        return Response(
            {"message": f"Successfully cleared {deleted_count} viewed startup(s)."},
            status=status.HTTP_200_OK
        )
    
    from django.http import Http404

    @extend_schema(
        description="Mark a startup as viewed (creates or updates viewed_at).",
        responses={200: StartupViewHistorySerializer}
    )
    @action(detail=True, methods=["post"], url_path="view", url_name="mark-viewed")
    def mark_as_viewed(self, request, pk=None):
        try:
            company = get_object_or_404(CompanyProfile, pk=pk)
        except (ValueError, TypeError):
            # If pk is not a number, return 404
            raise Http404("Invalid startup ID")

        self._check_permissions(request.user, company_id=pk)

        record_view(request.user, company)
        return Response({"message": "View recorded successfully."}, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Return the list of viewed startups for the authenticated user.",
        responses={200: StartupViewHistorySerializer(many=True)}
    )
    @action(detail=False, methods=["get"], url_path="viewed", url_name="viewed-history")
    def viewed(self, request):
        company_id = request.query_params.get("company_id", None)

        if company_id:
            self._check_permissions(request.user, company_id)
            queryset = StartupViewHistory.objects.filter(user=request.user, company_id=company_id)
        else:
            self._check_permissions(request.user)
            queryset = StartupViewHistory.objects.filter(user=request.user)

        queryset = queryset.order_by("-viewed_at")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)