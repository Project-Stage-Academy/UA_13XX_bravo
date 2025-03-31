from .views import (
    CompanyProfileViewSet,
    RegisterCompanyView,
    StartupViewHistoryViewSet,
    #FollowStartupView,
    #ListFollowedStartupsView,
    #nfollowStartupView,
    UserToCompanyViewSet
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

schema_urls = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

router = DefaultRouter()
router.register("company", CompanyProfileViewSet, basename="companyprofile")
router.register("user-to-company", UserToCompanyViewSet, basename="user-to-company")
router.register("startup-view-history", StartupViewHistoryViewSet, basename="startup-view-history")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterCompanyView.as_view(), name="register_company"),
    path("startups/<int:startup_id>/save/", FollowStartupView.as_view(), name="follow-startup"),
    path("investor/saved-startups/", ListFollowedStartupsView.as_view(), name="list-followed-startups"),
    path("startups/<int:startup_id>/unsave/", UnfollowStartupView.as_view(), name="unfollow-startup"),
    *schema_urls,
]
