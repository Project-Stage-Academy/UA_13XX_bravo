import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse
from notifications.models import Notification, NotificationPreference, Type
from notifications.serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
)

User = get_user_model()


@pytest.mark.django_db
class TestNotificationSerializers:
    @pytest.mark.parametrize(
        "content, expected_valid", [("", False), ("Valid content", True)]
    )
    def test_notification_serializer_validation(self, content, expected_valid):
        data = {"content": content, "read": False}
        serializer = NotificationSerializer(data=data)
        assert serializer.is_valid() == expected_valid

    @pytest.mark.parametrize(
        "type_name, expected_valid", [("Email", False), ("Push", True)]
    )
    def test_notification_preference_serializer_duplicate(
        self, test_user, type_name, expected_valid
    ):
        type_obj = Type.objects.create(name="Email")
        NotificationPreference.objects.create(user=test_user, type=type_obj)
        data = {"user": test_user.id, "type": type_name, "enabled": True}
        serializer = NotificationPreferenceSerializer(data=data)
        assert serializer.is_valid() == expected_valid

    @pytest.mark.parametrize(
        "type_name, expected_valid", [("Push", True), ("InvalidType", False)]
    )
    def test_notification_preference_serializer_invalid_type(
        self, test_user, type_name, expected_valid
    ):
        data = {"user": test_user.id, "type": type_name, "enabled": True}
        serializer = NotificationPreferenceSerializer(data=data)
        assert serializer.is_valid() == expected_valid


@pytest.mark.django_db
class TestNotificationViews:
    @pytest.mark.parametrize(
        "type_name, content, expected_status",
        [
            ("Push", "New alert", status.HTTP_201_CREATED),
            ("Push", "", status.HTTP_400_BAD_REQUEST),
        ],
    )
    def test_create_notification(
        self, api_client, test_user, type_name, content, expected_status
    ):
        api_client.force_authenticate(user=test_user)
        type_obj = Type.objects.create(name=type_name)
        url = reverse("notification-list")
        data = {"type": type_obj.id, "content": content}
        response = api_client.post(url, data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "initial_read_status, expected_final_status", [(False, True), (True, True)]
    )
    def test_mark_notification_as_read(
        self, api_client, test_user, initial_read_status, expected_final_status
    ):
        api_client.force_authenticate(user=test_user)
        type_obj = Type.objects.create(name="Push")
        notification = Notification.objects.create(
            user=test_user, type=type_obj, content="Test", read=initial_read_status
        )
        url = reverse("notification-mark-as-read", kwargs={"pk": notification.pk})
        response = api_client.patch(url, format="json")
        assert response.status_code == status.HTTP_200_OK
        notification.refresh_from_db()
        assert notification.read == expected_final_status


@pytest.mark.django_db
class TestIntegration:
    def test_notification_preferences_flow(self, api_client, test_user):
        api_client.force_authenticate(user=test_user)
        type_obj = Type.objects.create(name="Email")
        pref_url = reverse("notificationpreference-list")
        response = api_client.post(
            pref_url, {"type": "Email", "enabled": True}, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

        types_url = reverse("types-list")
        response = api_client.get(types_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0
