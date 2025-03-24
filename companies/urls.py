from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyProfileViewSet, RegisterCompanyView, StartupViewHistoryViewSe

router = DefaultRouter()
router.register(r"company", CompanyProfileViewSet, basename="companyprofile")
router.register(r"view-history", StartupViewHistoryViewSet, basename="startupviewhistory")


urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterCompanyView.as_view(), name="register_company"),
]