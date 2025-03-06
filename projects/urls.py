# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyProfileViewSet, UserToCompanyViewSet

router = DefaultRouter()
router.register(r"company-profiles", CompanyProfileViewSet, basename="companyprofile")
router.register(r"user-to-company", UserToCompanyViewSet, basename="usertocompany")

urlpatterns = [
    path("", include(router.urls)),
]
