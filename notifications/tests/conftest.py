import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from notifications.models import Type

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(email="apiuser@example.com", password="apipass")


@pytest.fixture
def notification_type(db):
    return Type.objects.create(name="Push")
