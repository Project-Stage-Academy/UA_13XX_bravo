import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from companies.models import CompanyProfile, StartupViewHistory
from users.models import User

@pytest.mark.django_db
def test_startup_view_history_unique(user, company):
    # Test uniqueness of views
    view_history_1 = StartupViewHistory.objects.create(user=user, company=company, viewed_at=timezone.now())
    assert view_history_1 is not None

    # Trying to create a duplicate view should raise an exception
    with pytest.raises(Exception):
        StartupViewHistory.objects.create(user=user, company=company, viewed_at=timezone.now())

@pytest.mark.django_db
def test_startup_view_history_creation(user, company):
    # Test creating a view record
    view_history = StartupViewHistory.objects.create(user=user, company=company, viewed_at=timezone.now())
    assert view_history.user == user
    assert view_history.company == company
    assert view_history.viewed_at is not None

@pytest.mark.django_db
def test_mark_as_viewed(client: APIClient, user: User, company: CompanyProfile):
    # Test for POST /api/v1/companies/view/{startup_id}
    client.force_authenticate(user=user)
    response = client.post(f"/api/v1/companies/view/{company.id}")
    assert response.status_code == status.HTTP_200_OK
    assert "View recorded successfully." in response.data

@pytest.mark.django_db
def test_get_viewed_history(client: APIClient, user: User, company: CompanyProfile):
    # Test for GET /api/v1/companies/viewed
    client.force_authenticate(user=user)
    client.post(f"/api/v1/companies/view/{company.id}")  # Record a view
    response = client.get("/api/v1/companies/viewed")
    assert response.status_code == status.HTTP_200_OK
    assert "startup_id" in response.data[0]
    assert "company_name" in response.data[0]
    assert "viewed_at" in response.data[0]

@pytest.mark.django_db
def test_clear_viewed_history(client: APIClient, user: User, company: CompanyProfile):
    # Test for DELETE /api/v1/companies/viewed/clear
    client.force_authenticate(user=user)
    client.post(f"/api/v1/companies/view/{company.id}")  # Record a view
    response = client.delete("/api/v1/companies/viewed/clear")
    assert response.status_code == status.HTTP_200_OK
    assert "Successfully cleared" in response.data["message"]

@pytest.mark.django_db
def test_investor_permission(client: APIClient, user: User, company: CompanyProfile):
    # Test for checking access only for investors
    user.role = "investor"  # Set the role in the User model
    user.save()
    client.force_authenticate(user=user)

    # Record a view
    client.post(f"/api/v1/companies/view/{company.id}")
    
    # Check access to viewed history
    response = client.get("/api/v1/companies/viewed")
    assert response.status_code == status.HTTP_200_OK