from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyProfileViewSet, FollowStartupView

router = DefaultRouter()
router.register(r"company", CompanyProfileViewSet, basename="companyprofile")

urlpatterns = [
    path("", include(router.urls)),
    path("startups/<int:startup_id>/save/", FollowStartupView.as_view(), name="follow-startup"),
]
