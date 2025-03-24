import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from notifications.models import Notification, Type, Entity
from notifications.serializers import NotificationSerializer
from notifications.views import NotificationViewSet


@pytest.mark.django_db
class TestNotificationSerializer:
    @pytest.mark.parametrize(
        "type_name, content, expected_valid",
        [
            ("Push", "Valid notification content", True),
            ("Email", "", False),
            ("InvalidType", "Valid content", False),
            ("Push", None, False),
            ("", "No type provided", False),
            ("Email", "Short", True),
            ("Push", "A" * 501, False),
            ("Push", "A" * 500, True),
            ("Email", "Valid email notification content", True),
            ("Email", None, False),
            ("Push", "", False),
            ("InvalidType", "", False),
        ],
    )
    def test_notification_serializer_validation(
        self, test_user, type_name, content, expected_valid
    ):
        if type_name and type_name != "InvalidType":
            Type.objects.get_or_create(name=type_name)

        factory = APIRequestFactory()
        request = factory.post("/")
        request.user = test_user

        data = {
            "user": test_user.id,
            "type": type_name,
            "content": content,
            "entity": None,
            "read": False,
        }

        serializer = NotificationSerializer(data=data, context={"request": request})
        assert serializer.is_valid() == expected_valid, serializer.errors

    def test_notification_serializer_creation_with_entity(self, test_user):
        type_push, _ = Type.objects.get_or_create(name="Push")
        entity_data = {"name": "Test Entity"}

        factory = APIRequestFactory()
        request = factory.post("/")
        request.user = test_user

        data = {
            "user": test_user.id,
            "type": "Push",
            "content": "Notification with entity",
            "entity": entity_data,
            "read": False,
        }

        serializer = NotificationSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        notification = serializer.save()

        assert Notification.objects.count() == 1
        assert Entity.objects.count() == 1
        assert notification.entity.name == "Test Entity"

    @pytest.mark.parametrize(
        "action,method,detail,status_code",
        [
            ("mark_as_read", "patch", True, 200),
            ("mark_as_unread", "patch", True, 200),
            ("mark_all_as_read", "patch", False, 200),
            ("mark_all_as_unread", "patch", False, 200),
        ],
    )
    def test_notification_actions(self, test_user, action, method, detail, status_code):
        type_push, _ = Type.objects.get_or_create(name="Push")
        notification = Notification.objects.create(
            user=test_user, type=type_push, content="Test", read=False
        )

        factory = APIRequestFactory()
        view = NotificationViewSet.as_view({method: action})
        url = f"/{action}/"

        data = {"id": notification.id} if detail else {}
        request_method = getattr(factory, method)
        request = request_method(url, data)
        force_authenticate(request, user=test_user)

        if detail:
            response = view(request, pk=notification.id)
        else:
            response = view(request)

        assert response.status_code == status_code

    def test_list_notifications(self, test_user):
        type_push, _ = Type.objects.get_or_create(name="Push")
        Notification.objects.create(
            user=test_user, type=type_push, content="Test notification"
        )

        factory = APIRequestFactory()
        view = NotificationViewSet.as_view({"get": "list"})

        request = factory.get("/")
        force_authenticate(request, user=test_user)
        response = view(request)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["content"] == "Test notification"

    def test_delete_notification(self, test_user):
        type_push, _ = Type.objects.get_or_create(name="Push")
        notification = Notification.objects.create(
            user=test_user, type=type_push, content="To delete"
        )

        factory = APIRequestFactory()
        view = NotificationViewSet.as_view({"delete": "destroy"})

        request = factory.delete(f"/{notification.id}/")
        force_authenticate(request, user=test_user)
        response = view(request, pk=notification.id)

        assert response.status_code == 204
        assert Notification.objects.count() == 0
