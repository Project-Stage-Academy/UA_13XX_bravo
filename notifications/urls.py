from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationPreferenceViewSet, TypesListView

router = DefaultRouter()
router.register(
    r"notifications/preferences",
    NotificationPreferenceViewSet,
    basename="notification_preferences",
)

urlpatterns = [
    path("", include(router.urls)),
    path("notifications/types/", TypesListView.as_view(), name="notification_types"),
]
