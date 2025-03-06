from django.shortcuts import render

# views.py
from rest_framework import viewsets
from .models import CompanyProfile, UserToCompany
from .serializers import CompanyProfileSerializer, UserToCompanySerializer
from rest_framework.permissions import IsAuthenticated


class CompanyProfileViewSet(viewsets.ModelViewSet):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]


class UserToCompanyViewSet(viewsets.ModelViewSet):
    queryset = UserToCompany.objects.all()
    serializer_class = UserToCompanySerializer
    permission_classes = [IsAuthenticated]
