from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CompanyProfile, UserToCompany, CompanyFollowers, CompanyType
from .serializers import CompanyProfileSerializer, UserToCompanySerializer, CompanyFollowersSerializer, CompanyRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
import logging
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
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


class InvestorStartupMixin:
    """
    Class for retrieving the investor's company and startup.
    """
    def get_investor_company(self, request):
        """Retrieve the investor's enterprise company or raise a permission error."""
        try:
            return request.user.company_memberships.get(company__type=CompanyType.ENTERPRISE).company
        except UserToCompany.DoesNotExist:
            if not request.user.company_memberships.exists():
                raise PermissionDenied("User is not associated with any company.")
            raise PermissionDenied("User is not linked to an enterprise company.")
    
    def get_startup(self, startup_id):
        """Retrieve a startup by ID or raise a not found error."""
        try:
            return get_object_or_404(CompanyProfile, id=startup_id, type=CompanyType.STARTUP)
        except Http404:
            raise NotFound({"error": "Startup not found."})

class FollowStartupView(APIView, InvestorStartupMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request, startup_id):
        """Allow an investor to follow a startup."""
        investor_company = self.get_investor_company(request)
        startup = self.get_startup(startup_id)

        if CompanyFollowers.objects.filter(investor=investor_company, startup=startup).exists():
            return Response({"detail": "You are already following this startup."}, status=status.HTTP_400_BAD_REQUEST)

        follow_relation = CompanyFollowers.objects.create(investor=investor_company, startup=startup)
        serializer = CompanyFollowersSerializer(follow_relation)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UnFollowStartupView(APIView, InvestorStartupMixin):
    """A view that allows an investor to unfollow a startup."""
    permission_classes = [IsAuthenticated]

    def post(self, request, startup_id):
        """
        Parameters:
        startup_id (int): The ID of the startup to unfollow.

        Response: 
        A success message if unfollowed, or an error message.
        """
        investor_company = self.get_investor_company(request)
        startup = self.get_startup(startup_id)

        unfollow_relation = CompanyFollowers.objects.filter(investor=investor_company, startup=startup)
        if not unfollow_relation.exists():
            return Response({"detail": "You are not following this startup."}, status=status.HTTP_400_BAD_REQUEST)

        unfollow_relation.delete()

        return Response({"detail": "Successfully unfollowed the startup."}, status=status.HTTP_200_OK)
    
class ListFollowedStartupsView(APIView, InvestorStartupMixin):
    """
    A view that lists all followed startups by an investor
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Responses:
        - 200 OK: Returns a list of followed startups.
        - 400 Bad Request: If the user is not linked to any company or is not an enterprise.

        Example Request:
        GET /api/investor/saved-startups?search=tech&order_by=-created_at
        """
        investor_company = self.get_investor_company(request)
        
        startups = CompanyProfile.objects.filter(
            startup_investors__investor=investor_company
        )
        search_query = request.query_params.get("search", None)
        order = request.query_params.get("order_by", "company_name")

        if search_query:
            startups = startups.filter(company_name__icontains=search_query)

        allowed_order_fields = ["company_name", "created_at", "description", "updated_at"]
        if order.lstrip("-") in allowed_order_fields:
            startups = startups.order_by(order)

        serializer = CompanyProfileSerializer(startups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)