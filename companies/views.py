from rest_framework import viewsets
from .models import CompanyProfile, UserToCompany
from .serializers import CompanyProfileSerializer, UserToCompanySerializer, CompanyRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
import logging


logger = logging.getLogger(__name__)


class CompanyProfileViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing CompanyProfile instances.

    Attributes:
        queryset (QuerySet): A queryset of all CompanyProfile instances.
        serializer_class (Serializer): The serializer class for CompanyProfile instances.
        permission_classes (list): A list of permission classes for the viewset.
    """
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]


class UserToCompanyViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing UserToCompany instances.

    Attributes:
        queryset (QuerySet): A queryset of all UserToCompany instances.
        serializer_class (Serializer): The serializer class for UserToCompany instances.
        permission_classes (list): A list of permission classes for the viewset.
    """
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

