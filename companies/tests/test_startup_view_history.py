import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from companies.models import StartupViewHistory
from companies.models import CompanyProfile  


@pytest.mark.django_db
def test_startup_view_history_unique(test_user, test_companies, api_client: APIClient):
    # Test uniqueness of views
    company = test_companies[0]  # Using the company from the fixture
    view_history_1 = StartupViewHistory.objects.create(user=test_user, company=company, viewed_at=timezone.now())
    assert view_history_1 is not None

    # Trying to create a duplicate view should raise an exception
    with pytest.raises(Exception):
        StartupViewHistory.objects.create(user=test_user, company=company, viewed_at=timezone.now())


@pytest.mark.django_db
def test_startup_view_history_creation(test_user, test_companies, api_client: APIClient):
    # Перевірка, чи компанії створені
    assert CompanyProfile.objects.exists(), "No companies were created in the database."
    
    company = test_companies[0]  # Using the company from the fixture
    view_history = StartupViewHistory.objects.create(user=test_user, company=company, viewed_at=timezone.now())
    assert view_history.user == test_user
    assert view_history.company == company
    assert view_history.viewed_at is not None


@pytest.mark.django_db
def test_mark_as_viewed(api_client: APIClient, test_user, test_companies):
    # Test for POST /api/v1/companies/view/{startup_id}
    company = test_companies[0]  # Using the company from the fixture
    api_client.force_authenticate(user=test_user)  # Authenticate the user
    response = api_client.post(f"/api/v1/companies/view/{company.id}/")  # Adds a trailing slash
    assert response.status_code == status.HTTP_200_OK
    assert "View recorded successfully." in response.data
    
    # Перевірка створення запису у StartupViewHistory
    view_history = StartupViewHistory.objects.filter(user=test_user, company=company)
    assert view_history.exists()  # Перевіряємо, що запис було створено
    assert view_history.first().viewed_at is not None  # Перевіряємо, що час перегляду був встановлений


@pytest.mark.django_db
def test_get_viewed_history(api_client: APIClient, test_user, test_companies):
    # Test for GET /api/v1/companies/viewed
    company = test_companies[0]  # Using the company from the fixture
    api_client.force_authenticate(user=test_user)  # Authenticate the user
    api_client.post(f"/api/v1/companies/view/{company.id}/")  # Adds a trailing slash to record a view
    response = api_client.get("/api/v1/companies/viewed")
    assert response.status_code == status.HTTP_200_OK
    assert "startup_id" in response.data[0]
    assert "company_name" in response.data[0]
    assert "viewed_at" in response.data[0]


@pytest.mark.django_db
def test_clear_viewed_history(api_client: APIClient, test_user, test_companies):
    # Test for DELETE /api/v1/companies/viewed/clear
    company = test_companies[0]  # Using the company from the fixture
    api_client.force_authenticate(user=test_user)  # Authenticate the user
    api_client.post(f"/api/v1/companies/view/{company.id}/")  # Adds a trailing slash to record a view
    response = api_client.delete("/api/v1/companies/viewed/clear")  # Clears the history
    assert response.status_code == status.HTTP_200_OK
    assert "Successfully cleared" in response.data["message"]
    
    # Перевірка, що всі записи історії були очищені
    assert not StartupViewHistory.objects.filter(user=test_user).exists()  # Історія має бути очищена

@pytest.mark.django_db
def test_investor_permission(api_client: APIClient, test_user, test_companies):
    # Тест для перевірки доступу лише для користувачів з доступом до компанії
    company = test_companies[0]  # Використовуємо компанію з фікстури

    # Спочатку задаємо користувачу роль "non_investor"
    test_user.role = "non_investor"
    test_user.save()
    api_client.force_authenticate(user=test_user)  # Аутентифікуємо користувача

    # Спробуємо отримати історію переглядів для компанії
    response = api_client.get(f"/api/v1/companies/viewed?company_id={company.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN  # Перевірка, що повертається 403 помилка

    # Перевірка, що користувач не має доступу до цієї компанії
    assert not UserToCompany.objects.filter(user=test_user, company=company).exists()

    # Тепер задаємо користувачу роль "investor"
    test_user.role = "investor"
    test_user.save()

    # Додаємо зв'язок користувача з компанією
    UserToCompany.objects.create(user=test_user, company=company)

    # Повторюємо тест з роллю "investor"
    api_client.force_authenticate(user=test_user)

    # Перевірка доступу до історії переглядів компанії
    response = api_client.get(f"/api/v1/companies/viewed?company_id={company.id}")
    assert response.status_code == status.HTTP_200_OK

    # Перевірка запису перегляду
    response = api_client.post(f"/api/v1/companies/view/{company.id}/")
    assert response.status_code == status.HTTP_200_OK