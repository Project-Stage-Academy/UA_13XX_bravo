from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyProfileViewSet, RegisterCompanyView
from .views import UserToCompanyViewSet  

router = DefaultRouter()
router.register(r"company", CompanyProfileViewSet, basename="companyprofile")
router.register(r"user-to-company", UserToCompanyViewSet, basename="user-to-company")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterCompanyView.as_view(), name="register_company"),
]
