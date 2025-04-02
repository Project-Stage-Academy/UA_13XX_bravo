import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse
from notifications.models import Notification, NotificationPreference, Type
from notifications.serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
)
from rest_framework.test import APIRequestFactory

User = get_user_model()


@pytest.mark.django_db
class TestNotificationSerializers:

    @pytest.mark.parametrize(
        "type_name, expected_valid", [("Email", False), ("Push", True)]
    )
    def test_notification_preference_serializer_duplicate(
        self, api_client, test_user, type_name, expected_valid
    ):
        # Authenticate the test client
        api_client.force_authenticate(user=test_user)

        # Ensure the required Type objects exist
        type_email, _ = Type.objects.get_or_create(name="Email")
        type_push, _ = Type.objects.get_or_create(name="Push")

        # Ensure the correct type object is retrieved using name
        type_obj = Type.objects.get(name=type_name)

        # ✅ Ensure an existing `NotificationPreference` is created before validation
        if type_name == "Email":
            NotificationPreference.objects.create(user=test_user, type=type_email)

        # ✅ Create a real request object
        factory = APIRequestFactory()
        request = factory.post("/")  # Dummy request (can be GET/POST)
        request.user = test_user  # Manually set authenticated user

        data = {"user": test_user.id, "type": type_obj.name, "enabled": True}
        serializer = NotificationPreferenceSerializer(
            data=data, context={"request": request}
        )

        assert serializer.is_valid() == expected_valid, serializer.errors

    @pytest.mark.parametrize(
        "type_name, expected_valid", [("Push", True), ("InvalidType", False)]
    )
    def test_notification_preference_serializer_invalid_type(
        self, test_user, type_name, expected_valid
    ):
        # Ensure that "Push" exists in the database before validation
        if type_name == "Push":
            Type.objects.get_or_create(name="Push")

        # Create a request to provide context for authentication
        factory = APIRequestFactory()
        request = factory.post("/")  # Dummy request (can be GET/POST)
        request.user = test_user  # Manually set authenticated user

        # Prepare data for the serializer (passing `type` as a string)
        data = {"user": test_user.id, "type": type_name, "enabled": True}
        serializer = NotificationPreferenceSerializer(
            data=data, context={"request": request}
        )

        # Validate and assert the result
        assert serializer.is_valid() == expected_valid, serializer.errors
