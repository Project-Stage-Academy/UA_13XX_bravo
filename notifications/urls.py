from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationPreferenceViewSet, TypesListView, NotificationViewSet, InvestorNotificationViewSet

router = DefaultRouter()
router.register(
    r"notifications/preferences",
    NotificationPreferenceViewSet,
    basename="notification_preferences",
)

router.register(
    r"notifications",
    NotificationViewSet,
    basename="notification",
)

router.register(
    r"investor/notifications",
    InvestorNotificationViewSet,
    basename="investor_notifications",
) 

urlpatterns = [
    path("notifications/types/", TypesListView.as_view(), name="notification_types"),
    path("", include(router.urls)),
]
