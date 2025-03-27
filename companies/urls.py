from .views import (
    CompanyProfileViewSet,
    RegisterCompanyView,
    StartupViewHistoryViewSet,
    FollowStartupView,
    ListFollowedStartupsView,
    UnfollowStartupView,
    UserToCompanyViewSet
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("company", CompanyProfileViewSet, basename="companyprofile")
router.register("user-to-company", UserToCompanyViewSet, basename="user-to-company")
router.register("view-history", StartupViewHistoryViewSet, basename="startupviewhistory")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterCompanyView.as_view(), name="register_company"),
    path("startups/<int:startup_id>/save/", FollowStartupView.as_view(), name="follow-startup"),
    path("investor/saved-startups/", ListFollowedStartupsView.as_view(), name="list-followed-startups"),
    path("startups/<int:startup_id>/unsave/", UnfollowStartupView.as_view(), name="unfollow-startup"),
    path("companies/view/<int:pk>/", StartupViewHistoryViewSet.as_view({'post': 'mark_as_viewed'}), name="view-startup"),
    path("companies/viewed", StartupViewHistoryViewSet.as_view({'get': 'list'}), name="viewed-history"),
    path("companies/viewed/clear", StartupViewHistoryViewSet.as_view({'delete': 'clear_view_history'}), name="clear-view-history"),
]
