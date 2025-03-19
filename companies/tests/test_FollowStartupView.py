from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from companies.models import CompanyProfile, CompanyFollowers, UserToCompany, CompanyType

class FollowStartupAPITest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.investor_user = User.objects.create_user(email="investor@example.com", password="testpass123!")
        self.investor_company = CompanyProfile.objects.create(company_name="Investor Corp", type=CompanyType.ENTERPRISE)
        UserToCompany.objects.create(user=self.investor_user, company=self.investor_company)

        self.startup = CompanyProfile.objects.create(company_name="Tech Startup", type=CompanyType.STARTUP)

        self.user_no_company = User.objects.create_user(email="no_company@example.com", password="testpass123!")

        self.non_investor_user = User.objects.create_user(email="non_investor@example.com", password="testpass123!")
        self.non_investor_company = CompanyProfile.objects.create(company_name="Regular Company", type=CompanyType.STARTUP)
        UserToCompany.objects.create(user=self.non_investor_user, company=self.non_investor_company)

    def test_follow_startup_success(self):
        """
        Test that an investor can successfully follow a startup.
        """
        self.client.force_authenticate(user=self.investor_user)
        response = self.client.post(f"/api/startups/{self.startup.id}/save/")
        assert response.status_code == status.HTTP_201_CREATED
        assert CompanyFollowers.objects.filter(investor=self.investor_company, startup=self.startup).exists()

    def test_follow_startup_already_following(self):
        """
        Test that attempting to follow a startup already followed returns a 400 error.
        """
        CompanyFollowers.objects.create(investor=self.investor_company, startup=self.startup)
        self.client.force_authenticate(user=self.investor_user)
        response = self.client.post(f"/api/startups/{self.startup.id}/save/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "You are already following this startup."

    def test_follow_startup_user_not_in_company(self):
        """
        Test that a user who is not linked to a company cannot follow a startup.
        """
        self.client.force_authenticate(user=self.user_no_company)
        response = self.client.post(f"/api/startups/{self.startup.id}/save/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "User must be linked to an enterprise company."

    def test_follow_startup_company_not_enterprise(self):
        """
        Test that a user linked to a non-enterprise company cannot follow a startup.
        """
        self.client.force_authenticate(user=self.non_investor_user)
        response = self.client.post(f"/api/startups/{self.startup.id}/save/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "User must be linked to an enterprise company."

    def test_follow_startup_not_found(self):
        """
        Test that attempting to follow a non-existent startup returns a 404 error.
        """
        self.client.force_authenticate(user=self.investor_user)
        response = self.client.post("/api/startups/999/save/")  
        assert response.status_code == status.HTTP_404_NOT_FOUND