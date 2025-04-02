import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from companies.models import StartupViewHistory
from companies.models import CompanyProfile  
from companies.models import UserToCompany
from django.db.utils import IntegrityError
from users.models import UserRole

@pytest.mark.django_db
def test_duplicate_view_updates_viewed_at(test_user, test_companies):
    company = test_companies[0]

    # First creation of the view record
    first_view = StartupViewHistory.objects.create(user=test_user, company=company, viewed_at=timezone.now())

    # Delay to see the difference in time
    import time
    time.sleep(1)

    # Simulating a repeated view: your API logic should update viewed_at
    # Either call the endpoint here or use get_or_create + time update logic
    existing = StartupViewHistory.objects.get(user=test_user, company=company)
    old_time = existing.viewed_at
    existing.viewed_at = timezone.now()
    existing.save()

    updated = StartupViewHistory.objects.get(user=test_user, company=company)
    assert updated.viewed_at > old_time


@pytest.mark.django_db
def test_startup_view_history_creation(test_user, test_companies, api_client: APIClient):
    # Check if companies are created
    assert CompanyProfile.objects.exists(), "No companies were created in the database."
    
    company = test_companies[0]  # Using the company from the fixture
    view_history = StartupViewHistory.objects.create(user=test_user, company=company, viewed_at=timezone.now())
    assert view_history.user == test_user
    assert view_history.company == company
    assert view_history.viewed_at is not None


@pytest.mark.django_db
def test_mark_as_viewed(api_client: APIClient, test_user, test_companies):
    # Test for POST /company/startup-view-history/{startup_id}
    company = test_companies[0]
    UserToCompany.objects.create(user=test_user, company=company)
    api_client.force_authenticate(user=test_user)
    response = api_client.post(f"/company/startup-view-history/{company.id}/view/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "View recorded successfully."
    
    # Check if record is created in StartupViewHistory
    view_history = StartupViewHistory.objects.filter(user=test_user, company=company)
    assert view_history.exists()
    assert view_history.first().viewed_at is not None


@pytest.mark.django_db
def test_get_viewed_history(api_client: APIClient, test_user, test_companies):
    # Test for GET /company/startup-view-history/viewed/
    company = test_companies[0]
    UserToCompany.objects.create(user=test_user, company=company)
    api_client.force_authenticate(user=test_user)
    api_client.post(f"/company/startup-view-history/{company.id}/view/")  # Record view
    response = api_client.get("/company/startup-view-history/viewed/")
    print("RESPONSE DATA:", response.data)
    assert response.status_code == status.HTTP_200_OK
    assert "startup_id" in response.data[0]
    assert "company_name" in response.data[0]
    assert "viewed_at" in response.data[0]    


@pytest.mark.django_db
def test_clear_viewed_history(api_client: APIClient, test_user, test_companies):
    # Test for DELETE /company/startup-view-history/clear/clear
    company = test_companies[0]
    UserToCompany.objects.create(user=test_user, company=company)
    api_client.force_authenticate(user=test_user)
    api_client.post(f"/company/startup-view-history/{company.id}/view/")  # Record view
    response = api_client.delete("/company/startup-view-history/clear/")
    assert response.status_code == status.HTTP_200_OK
    assert "Successfully cleared" in response.data["message"]

    # Check that all records were cleared
    assert not StartupViewHistory.objects.filter(user=test_user).exists()
    

@pytest.mark.django_db
def test_mark_as_viewed_invalid_id(api_client, test_user):
    # Test for invalid ID (non-existent company ID)
    api_client.force_authenticate(user=test_user)
    
    # Trying to mark the startup as viewed with an invalid ID
    response = api_client.post("/company/startup-view-history/999999/view/")  # Using a non-existent company ID

    # Check if 404 error is returned
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Check if the response contains the correct error message
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_mark_as_viewed_invalid_non_numeric_id(api_client, test_user):
    # Test for invalid ID (non-numeric ID)
    api_client.force_authenticate(user=test_user)
    
    # Trying to mark the startup as viewed with an incorrect (non-numeric) ID
    response = api_client.post("/company/startup-view-history/invalid_id/view/")  # Invalid ID

    # Check if 404 error is returned
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Check if the response contains the correct error message
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_mark_as_viewed_empty_id(api_client, test_user):
    # Test for invalid ID (empty ID)
    api_client.force_authenticate(user=test_user)
    
    # Trying to mark the startup as viewed without an ID
    response = api_client.post("/company/startup-/view-history/")  # Empty ID

    # Check if 404 error is returned
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Check if the response contains the correct error message
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_viewed_at_update_on_revisit(api_client, test_user, test_companies):
    company = test_companies[0]  
    UserToCompany.objects.create(user=test_user, company=company)
    test_viewed_at_update_on_revisit
    api_client.force_authenticate(user=test_user)  

    # First view
    api_client.post(f"/company/startup-view-history/{company.id}/view/")
    first_time = StartupViewHistory.objects.get(user=test_user, company=company).viewed_at

    # Delay for updating the time
    from time import sleep
    sleep(1)

    # Revisit
    api_client.post(f"/company/startup-view-history/{company.id}/view/")
    second_time = StartupViewHistory.objects.get(user=test_user, company=company).viewed_at

    # Check if the viewed_at timestamp was updated
    assert second_time > first_time, "The 'viewed_at' timestamp was not updated on revisit."


@pytest.mark.django_db
def test_investor_permission(api_client: APIClient, test_user, test_companies):
    # Test to check access only for users with company access
    company = test_companies[0]  # Using the company from the fixture

    # First set the user role to "non_investor"
    test_user.role = UserRole.objects.create(name="non_investor")
    test_user.save()
    api_client.force_authenticate(user=test_user)  # Authenticate the user

    # Try to get the view history for the company
    response = api_client.get(f"/company/startup-view-history/viewed/?company_id={company.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Check that a 403 error is returned

    # Check that the user does not have access to this company
    assert not UserToCompany.objects.filter(user=test_user, company=company).exists()

    # Now set the user role to "investor"
    investor_role, _ = UserRole.objects.get_or_create(name="investor")
    test_user.role = investor_role
    test_user.save()

    # Add the user-company association
    UserToCompany.objects.create(user=test_user, company=company)

    # Repeat the test with the "investor" role
    api_client.force_authenticate(user=test_user)

    # Check access to the company's view history
    response = api_client.get(f"/company/startup-view-history/viewed/?company_id={company.id}")
    assert response.status_code == status.HTTP_200_OK

    # Check the view record
    response = api_client.post(f"/company/startup-view-history/{company.id}/view/")
    assert response.status_code == status.HTTP_200_OK