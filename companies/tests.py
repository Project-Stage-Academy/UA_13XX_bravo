# companies/test_companies.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from companies.models import CompanyProfile, UserToCompany

User = get_user_model()


@pytest.mark.django_db
class TestCompanies:
    """
    4 model tests + 8 API tests = 12 tests in total.
    """

    # ======== MODEL TESTS ========

    def test_company_profile_creation(self):
        """Test that a CompanyProfile instance is created successfully."""
        company = CompanyProfile.objects.create(
            company_name="Test Company",
            description="Some description",
            website="https://example.com",
        )
        assert company.pk is not None

    def test_company_profile_str(self):
        """Test the __str__ method of CompanyProfile."""
        company = CompanyProfile.objects.create(
            company_name="Str Company", description="Description"
        )
        assert str(company) == "Str Company"

    def test_user_to_company_creation(self):
        """Test that a UserToCompany instance is created successfully."""
        user = User.objects.create_user(username="modeluser", password="12345")
        company = CompanyProfile.objects.create(
            company_name="CompanyX", description="Desc"
        )
        utc = UserToCompany.objects.create(user=user, company=company)
        assert utc.pk is not None

    def test_user_to_company_str(self):
        """Test the __str__ method of UserToCompany."""
        user = User.objects.create_user(username="relationuser", password="12345")
        company = CompanyProfile.objects.create(
            company_name="CompanyY", description="Desc"
        )
        utc = UserToCompany.objects.create(user=user, company=company)
        assert str(utc) == "relationuser - CompanyY"

    # ======== API TESTS ========

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def test_user(self):
        return User.objects.create_user(username="apiuser", password="apipass")

    def test_create_company_profile(self, api_client, test_user):
        """Test creating a CompanyProfile via POST /company/."""
        api_client.force_authenticate(user=test_user)
        url = reverse("companyprofile-list")
        data = {
            "company_name": "New Startup",
            "description": "Cool startup",
            "website": "https://startup.example.com",
            "startup_logo": "https://startup.example.com/logo.png",
            "type": "startup",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert CompanyProfile.objects.filter(company_name="New Startup").exists()

    def test_list_company_profiles(self, api_client, test_user):
        """Test listing all CompanyProfiles via GET /company/."""
        CompanyProfile.objects.create(company_name="List1", description="Desc")
        CompanyProfile.objects.create(company_name="List2", description="Desc")
        api_client.force_authenticate(user=test_user)
        url = reverse("companyprofile-list")
        response = api_client.get(url, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_company_profile(self, api_client, test_user):
        """Test retrieving a single CompanyProfile via GET /company/{pk}/."""
        company = CompanyProfile.objects.create(
            company_name="Retrieve Co", description="Desc"
        )
        api_client.force_authenticate(user=test_user)
        url = reverse("companyprofile-detail", kwargs={"pk": company.pk})
        response = api_client.get(url, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["company_name"] == "Retrieve Co"

    def test_update_company_profile(self, api_client, test_user):
        """Test full update (PUT) of a CompanyProfile via PUT /company/{pk}/."""
        company = CompanyProfile.objects.create(
            company_name="Old Name", description="Old Desc"
        )
        api_client.force_authenticate(user=test_user)
        url = reverse("companyprofile-detail", kwargs={"pk": company.pk})
        data = {"company_name": "Updated Name", "description": "Updated Desc"}
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        company.refresh_from_db()
        assert company.company_name == "Updated Name"
        assert company.description == "Updated Desc"

    def test_partial_update_company_profile(self, api_client, test_user):
        """Test partial update (PATCH) of a CompanyProfile via PATCH /company/{pk}/."""
        company = CompanyProfile.objects.create(
            company_name="Partial Up", description="Initial Desc"
        )
        api_client.force_authenticate(user=test_user)
        url = reverse("companyprofile-detail", kwargs={"pk": company.pk})
        data = {"description": "Only desc changed"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        company.refresh_from_db()
        assert company.description == "Only desc changed"

    def test_delete_company_profile(self, api_client, test_user):
        """Test deleting a CompanyProfile via DELETE /company/{pk}/."""
        company = CompanyProfile.objects.create(
            company_name="Delete Me", description="Desc"
        )
        api_client.force_authenticate(user=test_user)
        url = reverse("companyprofile-detail", kwargs={"pk": company.pk})
        response = api_client.delete(url, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CompanyProfile.objects.filter(pk=company.pk).exists()

    def test_unauthorized_create_company_profile(self, api_client):
        """Test that creating a CompanyProfile is forbidden without authentication."""
        url = reverse("companyprofile-list")
        data = {"company_name": "Unauthorized Co", "description": "Desc"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthorized_delete_company_profile(self, api_client):
        """Test that deleting a CompanyProfile is forbidden without authentication."""
        company = CompanyProfile.objects.create(
            company_name="Unauthorized Delete", description="Desc"
        )
        url = reverse("companyprofile-detail", kwargs={"pk": company.pk})
        response = api_client.delete(url, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert CompanyProfile.objects.filter(pk=company.pk).exists()
