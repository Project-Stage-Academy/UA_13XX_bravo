import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from companies.models import CompanyProfile
from projects.models import Project

User = get_user_model()

@pytest.fixture
def api_client():
    """Returns DRF test API client"""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Creates and returns a basic test user"""
    return User.objects.create_user(
        email="apiuser@example.com",
        password="apipass"
    )


@pytest.fixture
def another_user(db):
    """Creates and returns another test user"""
    return User.objects.create_user(
        email="another@example.com",
        password="testpass123"
    )


@pytest.fixture
def test_company_with_user(db):
    """Creates a valid CompanyProfile instance (without creator)"""
    return CompanyProfile.objects.create(
        company_name="TestCompany",
        description="Test Description",
        website="https://test.com"
    )


@pytest.fixture
def test_project(test_company_with_user):
    """Creates a Project linked to test_company_with_user"""
    return Project.objects.create(
        name="Test Project",
        status="active",
        required_funding=100000,
        raised_amount=0,
        company=test_company_with_user
    )