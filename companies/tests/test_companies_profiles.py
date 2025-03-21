import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from companies.models import CompanyProfile, UserToCompany
from django.db import transaction

User = get_user_model()

# === MODEL TESTS ===

@pytest.mark.django_db
def test_user_to_company_relation_creation():
    user = User.objects.create_user(
        email="utc@example.com",
        password="securepass123"
    )
    company = CompanyProfile.objects.create(
        company_name="Test Company UTC",
        description="Testing user to company relation"
    )
    relation = UserToCompany.objects.create(user=user, company=company)

    assert relation.pk is not None
    assert str(relation) == f"{user} - {company}"


@pytest.mark.django_db
def test_company_profile_creation_minimal():
    company = CompanyProfile.objects.create(
        company_name="Test Company",
        description="A description for test company",
        website="https://example.com"
    )

    assert company.pk is not None
    assert company.company_name == "Test Company"
    assert company.description == "A description for test company"
    assert company.website == "https://example.com"
    assert company.startup_logo == ""
    assert company.type == ""
    assert company.company_size is None
    assert company.phone_number is None


@pytest.mark.django_db
def test_company_profile_creation_full():
    company = CompanyProfile.objects.create(
        company_name="Full Co",
        description="Full data",
        website="https://fullco.com",
        startup_logo="https://fullco.com/logo.png",
        type="startup"
    )

    assert company.pk is not None
    assert company.company_name == "Full Co"
    assert company.description == "Full data"
    assert company.website == "https://fullco.com"
    assert company.startup_logo == "https://fullco.com/logo.png"
    assert company.type == "startup"


@pytest.mark.django_db
def test_user_to_company_duplicate_prevention(another_user):
    company = CompanyProfile.objects.create(
        company_name="Dup Co",
        description="Dup"
    )

    UserToCompany.objects.create(user=another_user, company=company)

    with pytest.raises(Exception):
        with transaction.atomic():
            UserToCompany.objects.create(user=another_user, company=company)
                    
# === AUTHENTICATED API TESTS ===


@pytest.mark.django_db
def test_company_profile_list_authenticated(api_client, test_user):
    CompanyProfile.objects.create(company_name="VisibleCo", description="Auth can see")
    api_client.force_authenticate(user=test_user)

    url = reverse("companyprofile-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert any(item["company_name"] == "VisibleCo" for item in response.json()["results"])


@pytest.mark.django_db
def test_company_profile_search(api_client, test_user, test_companies):
    api_client.force_authenticate(user=test_user)
    url = reverse("companyprofile-list") + "?search=Beta"
    response = api_client.get(url)

    assert response.status_code == 200
    assert any("Beta" in company["company_name"] for company in response.json()["results"])
    

@pytest.mark.django_db
def test_company_profile_filter(api_client, test_user):
    CompanyProfile.objects.create(company_name="SaaS Corp", description="B2B", type="startup")
    CompanyProfile.objects.create(company_name="Enterprise Inc", description="Infra", type="enterprise")
    api_client.force_authenticate(user=test_user)
    response = api_client.get("/api/company/?type=startup")
    assert response.status_code == 200
    assert all(company["type"] == "startup" for company in response.json()["results"])


@pytest.mark.django_db
def test_company_profile_ordering(api_client, test_user):
    CompanyProfile.objects.create(company_name="Small Co", company_size=5)
    CompanyProfile.objects.create(company_name="Big Co", company_size=100)
    CompanyProfile.objects.create(company_name="No Size Co")  # company_size=None

    api_client.force_authenticate(user=test_user)

    # Ascending
    response = api_client.get(reverse("companyprofile-list") + "?ordering=company_size")
    assert response.status_code == 200
    sizes = [c["company_size"] for c in response.json()["results"] if c["company_size"] is not None]
    assert sizes == sorted(sizes)

    # Descending
    response = api_client.get(reverse("companyprofile-list") + "?ordering=-company_size")
    assert response.status_code == 200
    sizes_desc = [c["company_size"] for c in response.json()["results"] if c["company_size"] is not None]
    assert sizes_desc == sorted(sizes_desc, reverse=True)


@pytest.mark.django_db
def test_company_profile_pagination(api_client, test_user):
    for i in range(15):
        CompanyProfile.objects.create(company_name=f"Company{i}", description=f"Desc {i}")
    api_client.force_authenticate(user=test_user)
    response = api_client.get("/api/company/?limit=10&offset=0")
    assert response.status_code == 200
    assert "results" in response.json()
    assert len(response.json()["results"]) == 10


@pytest.mark.django_db
def test_company_profile_detail_authenticated(api_client, test_user):
    company = CompanyProfile.objects.create(
        company_name="DetailCo",
        description="Detail View Test",
        type="startup"
    )
    api_client.force_authenticate(user=test_user)
    response = api_client.get(f"/api/company/{company.id}/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "DetailCo"
    assert data["description"] == "Detail View Test"
    assert data["type"] == "startup"
    
# === UNAUTHORIZED ACCESS TESTS ===

@pytest.mark.django_db
def test_unauthorized_company_list_access():
    client = APIClient()
    url = reverse("companyprofile-list")
    response = client.get(url)
    assert response.status_code == 401
    

@pytest.mark.django_db
def test_company_access_by_authenticated_user(api_client, django_user_model):
    """
    Even if the user is not related to the company, they should still have access
    to the company list because all authenticated users are allowed to view it.
    """
    user = django_user_model.objects.create_user(
        email="openaccess@example.com",
        password="pass12345"
    )
    CompanyProfile.objects.create(
        company_name="Public Co",
        description="Visible to all authenticated users"
    )

    api_client.force_authenticate(user=user)
    url = reverse("companyprofile-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert any(
        company["company_name"] == "Public Co"
        for company in response.json()["results"]
    )


@pytest.mark.django_db
def test_unauthorized_company_creation():
    client = APIClient()
    url = reverse("companyprofile-list")
    data = {
        "company_name": "Unauthorized Company",
        "description": "Should not work",
        "type": "startup"
    }
    response = client.post(url, data=data, format="json")
    assert response.status_code == 401
    
    
@pytest.mark.django_db
def test_unauthorized_company_detail_access():
    company = CompanyProfile.objects.create(
        company_name="PrivateCo",
        description="Should be protected"
    )
    client = APIClient()
    url = reverse("companyprofile-detail", kwargs={"pk": company.id})
    response = client.get(url)
    assert response.status_code == 401