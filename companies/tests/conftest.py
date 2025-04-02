import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from companies.models import CompanyProfile
from users.models import User, UserRole

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    user = User.objects.create_user(email="apiuser@example.com", password="testpass123")
    investor_role, _ = UserRole.objects.get_or_create(name="investor")
    user.role = investor_role
    user.save()
    return user


@pytest.fixture
def test_companies(db):
    """
    This fixture creates test companies for use in the tests.
    It returns a list of CompanyProfile objects.
    """
    companies = [
        CompanyProfile.objects.create(company_name="AlphaTech", description="AI"),
        CompanyProfile.objects.create(company_name="BetaSoft", description="Cloud"),
    ]
    return companies


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="another@example.com",
        password="testpass123"
    )