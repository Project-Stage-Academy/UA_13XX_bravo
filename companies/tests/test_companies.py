import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from companies.models import CompanyProfile, UserToCompany

User = get_user_model()


@pytest.mark.django_db
class TestCompanies:
    """
    4 model tests + 8 API tests = 12 tests in total.
    """

    # ======== MODEL TESTS ========

    @pytest.mark.parametrize(
        "company_name, description, website",
        [
            ("Test Company", "Some description", "https://example.com"),
            ("Str Company", "Description", None),
        ],
    )
    def test_company_profile_creation(self, company_name, description, website):
        """Test that a CompanyProfile instance is created successfully."""
        company = CompanyProfile.objects.create(
            company_name=company_name, description=description, website=website
        )
        assert company.pk is not None
        assert company.company_name == company_name
        assert company.description == description
        assert company.website == website
        assert company.startup_logo == ""
        assert company.type == ""

    @pytest.mark.parametrize(
        "username, password, company_name",
        [
            ("modeluser", "12345", "CompanyX"),
            ("relationuser", "12345", "CompanyY"),
        ],
    )
    def test_user_to_company_creation(self, username, password, company_name):
        """Test that a UserToCompany instance is created successfully."""
        user = User.objects.create_user(username=username, password=password)
        company = CompanyProfile.objects.create(
            company_name=company_name, description="Desc"
        )
        utc = UserToCompany.objects.create(user=user, company=company)
        assert utc.pk is not None
        assert str(utc) == f"{username} - {company_name}"

    # ======== API TESTS ========

    @pytest.mark.parametrize(
        "method, url_name, data, expected_status",
        [
            ("get", "companyprofile-list", None, status.HTTP_200_OK),  # List
            (
                "post",
                "companyprofile-list",
                {  # Create
                    "company_name": "New Startup",
                    "description": "Cool startup",
                    "website": "https://startup.example.com",
                    "startup_logo": "https://startup.example.com/logo.png",
                    "type": "startup",
                },
                status.HTTP_201_CREATED,
            ),
            ("get", "companyprofile-detail", None, status.HTTP_200_OK),  # Retrieve
            (
                "put",
                "companyprofile-detail",
                {  # Full Update
                    "company_name": "Updated Name",
                    "description": "Updated Desc",
                },
                status.HTTP_200_OK,
            ),
            (
                "patch",
                "companyprofile-detail",
                {  # Partial Update
                    "description": "Only desc changed",
                },
                status.HTTP_200_OK,
            ),
            (
                "delete",
                "companyprofile-detail",
                None,
                status.HTTP_204_NO_CONTENT,
            ),  # Delete
        ],
    )
    def test_company_profile_operations(
        self, api_client, test_user, method, url_name, data, expected_status
    ):
        """
        Test listing, creating, retrieving, updating, and deleting CompanyProfile using parametrize.
        """
        company = CompanyProfile.objects.create(
            company_name="Test Company", description="Desc"
        )

        api_client.force_authenticate(user=test_user)
        url = reverse(
            url_name, kwargs={"pk": company.pk} if "detail" in url_name else {}
        )
        response = getattr(api_client, method)(url, data, format="json")

        assert response.status_code == expected_status

        if method in ["put", "patch"]:
            company.refresh_from_db()
            for key, value in data.items():
                assert getattr(company, key) == value

    @pytest.mark.parametrize(
        "method, url_name, data, expected_status",
        [
            (
                "post",
                "companyprofile-list",
                {"company_name": "Unauthorized Co", "description": "Desc"},
                status.HTTP_401_UNAUTHORIZED,
            ),
            ("delete", "companyprofile-detail", None, status.HTTP_401_UNAUTHORIZED),
        ],
    )
    def test_unauthorized_company_profile_operations(
        self, api_client, method, url_name, data, expected_status
    ):
        """
        Test that unauthorized users cannot create or delete a CompanyProfile.
        """
        company = CompanyProfile.objects.create(
            company_name="Unauthorized Delete", description="Desc"
        )
        url = reverse(
            url_name, kwargs={"pk": company.pk} if "detail" in url_name else {}
        )
        response = getattr(api_client, method)(url, data, format="json")

        assert response.status_code == expected_status
        assert (
            CompanyProfile.objects.filter(pk=company.pk).exists()
            if method == "delete"
            else True
        )
