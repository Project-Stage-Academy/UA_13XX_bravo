from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from companies.models import CompanyProfile, UserToCompany, CompanyFollowers
from rest_framework import status

User = get_user_model()

class UnFollowStartupTests(APITestCase):
    def setUp(self):
        #creating users
        self.investor = User.objects.create_user(email="investor@example.com", password="oldpassword")
        self.investor_company = CompanyProfile.objects.create(company_name="Investor Company", description="Company to invest in startups", type="enterprise")
        UserToCompany.objects.create(user=self.investor, company=self.investor_company)

        self.startup1 = User.objects.create_user(email="startup1@example.com", password="oldpassword")
        self.startup1_company = CompanyProfile.objects.create(company_name="Startup 1", description="Company to test products", type="startup")
        UserToCompany.objects.create(user=self.startup1, company=self.startup1_company)

        #following startups
        CompanyFollowers.objects.create(investor=self.investor_company, startup=self.startup1_company)

        #authorizing to system as investor
        self.refresh = RefreshToken.for_user(self.investor)
        self.access_token = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.url = f"/api/startups/{self.startup1_company.id}/unsave/"
        self.response = self.client.post(self.url)
    
    def test_unfollow_startup_success(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.response.data['detail'], "Successfully unfollowed the startup.")

    def test_follow_startup_already_unfollowing(self):
        self.client.post(self.url)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You are not following this startup.")

    def test_unfollow_startup_unauthorized(self):
        self.client.credentials() 
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    def test_unfollow_startup_error_token(self):
        refresh = RefreshToken.for_user(self.startup1)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "User is not linked to an enterprise company.")

    def test_unfollow_startup_not_found(self):
        invalid_id = CompanyProfile.objects.latest("id").id + 999
        url = f"/api/startups/{invalid_id}/unsave/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfollow_not_followed_startup(self):
        other_startup = CompanyProfile.objects.create(company_name="Other", type="startup")
        url = f"/api/startups/{other_startup.id}/unsave/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You are not following this startup.")
