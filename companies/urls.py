from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyProfileViewSet,
    RegisterCompanyView,
    UserToCompanyViewSet,
)


router = DefaultRouter()
router.register(r"company", CompanyProfileViewSet, basename="companyprofile")
router.register(r"user-to-company", UserToCompanyViewSet, basename="user-to-company")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterCompanyView.as_view(), name="register_company"),
    # path("startups/<int:startup_id>/save/", FollowStartupView.as_view(), name="follow-startup"),
    # path("investor/saved-startups", ListFollowedStartupsView.as_view(), name='list-followed-stastups'),
    # path("startups/<int:startup_id>/unsave/", UnFollowStartupView.as_view(), name="unfollow-startup"),
]
