from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from companies.models import CompanyProfile, CompanyFollowers

class FollowStartupAPITest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(email="investor@example.com", password="testpass123!")
        self.client.force_authenticate(user=self.user)

        self.investor = CompanyProfile.objects.create(company_name="VC Firm", type="enterprise")
        self.startup = CompanyProfile.objects.create(company_name="Tech Startup", type="startup")

        self.user.company_memberships.create(company=self.investor)  # Прив'язуємо користувача до інвестора

    def test_follow_startup_successfully(self):
        """Test that an investor can successfully follow a startup."""
        response = self.client.post(f"/api/startups/{self.startup.id}/save/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CompanyFollowers.objects.count(), 1)
        print("Response status:", response.status_code)
        print("Response data:", response.json())    

    def test_follow_startup_already_followed(self):
        """Test that an investor cannot follow the same startup twice."""
        CompanyFollowers.objects.create(investor=self.investor, startup=self.startup)
        response = self.client.post(f"/api/startups/{self.startup.id}/save/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You are already following this startup.")
        print("Response status:", response.status_code)
        print("Response data:", response.json())
