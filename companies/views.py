from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CompanyProfile, UserToCompany, CompanyFollowers
from .serializers import CompanyProfileSerializer, UserToCompanySerializer, CompanyFollowersSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError


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

class FollowStartupView(APIView):
    def post(self, request, startup_id):
        """Allow an investor to follow a startup."""
        try:
            investor_company = request.user.company_memberships.get(company__type="enterprise")
            investor_id = investor_company.company.id
        except UserToCompany.DoesNotExist:
            return Response({"error": "User must be linked to an enterprise company."}, status=400)
        startup = get_object_or_404(CompanyProfile, id=startup_id, type="startup")
        investor = get_object_or_404(CompanyProfile, id=investor_id, type="enterprise")

        if CompanyFollowers.objects.filter(investor=investor, startup=startup).exists():
            return Response({"detail": "You are already following this startup."}, status=status.HTTP_400_BAD_REQUEST)

        follow_relation = CompanyFollowers.objects.create(investor=investor, startup=startup)
        serializer = CompanyFollowersSerializer(follow_relation)

        return Response(serializer.data, status=status.HTTP_201_CREATED)