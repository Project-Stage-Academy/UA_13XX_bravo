from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyProfileViewSet

router = DefaultRouter()
router.register(r"company", CompanyProfileViewSet, basename="companyprofile")

urlpatterns = [
    path("", include(router.urls)),
]
