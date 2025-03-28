import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from companies.models import CompanyProfile

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email="apiuser@example.com",
        password="apipass"
    )


@pytest.fixture
def test_companies(db):
    return [
        CompanyProfile.objects.create(company_name="AlphaTech", description="AI"),
        CompanyProfile.objects.create(company_name="BetaSoft", description="Cloud"),
    ]
    
    
@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="another@example.com",
        password="testpass123"
    )