from django.test import TestCase
from .models import CompanyProfile


class CompanyProfileTest(TestCase):
    def test_profile_creation(self):
        profile = CompanyProfile.objects.create(
            company_name="" "Test Company",
            description="A test startup",
            website="http://example.com",
        )
        self.assertEqual(profile.company_name, "Test Company")


from rest_framework.test import APITestCase
from django.urls import reverse


class CompanyProfileAPITest(APITestCase):
    def test_create_profile(self):
        url = reverse("companyprofile-list")
        data = {
            "company_name": "Test Company",
            "description": "Test description",
            "website": "http://example.com",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
