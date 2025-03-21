from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyProfileViewSet, RegisterCompanyView, FollowStartupView, ListFollowedStartupsView

router = DefaultRouter()
router.register(r"company", CompanyProfileViewSet, basename="companyprofile")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterCompanyView.as_view(), name="register_company"),
    path("startups/<int:startup_id>/save/", FollowStartupView.as_view(), name="follow-startup"),
    path("investor/saved-startups", ListFollowedStartupsView.as_view(), name='list-followed-stastups')
]
