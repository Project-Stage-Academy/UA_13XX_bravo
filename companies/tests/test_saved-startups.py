from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from companies.models import CompanyProfile, UserToCompany, CompanyFollowers
from rest_framework import status

User = get_user_model()

class SavedStartupsTests(APITestCase):
    def setUp(self):
        #creating users
        self.investor = User.objects.create_user(email="investor@example.com", password="oldpassword")
        self.investor_company = CompanyProfile.objects.create(company_name="Investor Company", description="Company to invest in startups", type="enterprise")
        UserToCompany.objects.create(user=self.investor, company=self.investor_company)

        self.startup1 = User.objects.create_user(email="startup1@example.com", password="oldpassword")
        self.startup1_company = CompanyProfile.objects.create(company_name="Startup 1", description="Company to test products", type="startup")
        UserToCompany.objects.create(user=self.startup1, company=self.startup1_company)

        self.startup2 = User.objects.create_user(email="startup2@example.com", password="oldpassword")
        self.startup2_company = CompanyProfile.objects.create(company_name="Startup 2", description="AI startup", type="startup")
        UserToCompany.objects.create(user=self.startup2, company=self.startup2_company)

        #following startups
        CompanyFollowers.objects.create(investor=self.investor_company, startup=self.startup1_company)
        CompanyFollowers.objects.create(investor=self.investor_company, startup=self.startup2_company)

        #authorizing to system as investor
        self.refresh = RefreshToken.for_user(self.investor)
        self.access_token = str(self.refresh.access_token)

    def test_get_saved_startups(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get("/api/investor/saved-startups")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(len(response.data), 2)

        for startup in response.data:
            self.assertIn("id", startup)
            self.assertIn("company_name", startup)
            self.assertIn("description", startup)
            self.assertIn("website", startup)
            self.assertIn("startup_logo", startup)

        startup_names = {startup["company_name"] for startup in response.data}
        self.assertSetEqual(startup_names, {"Startup 1", "Startup 2"})

        startup_descriptions = {startup["description"] for startup in response.data}
        self.assertSetEqual(startup_descriptions, {"Company to test products", "AI startup"})

    def test_get_saved_startups_search(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get("/api/investor/saved-startups?search=Startup 2")

        startup_names = {startup["company_name"] for startup in response.data}
        self.assertSetEqual(startup_names, {"Startup 2"})
        startup_descriptions = {startup["description"] for startup in response.data}
        self.assertSetEqual(startup_descriptions, {"AI startup"})

    def test_get_saved_startups_order_by(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get("/api/investor/saved-startups?order_by=-created_at")

        startup_names = [startup["company_name"] for startup in response.data]
        self.assertEqual(startup_names, ["Startup 2", "Startup 1"])  
        startup_descriptions = {startup["description"] for startup in response.data}
        self.assertSetEqual(startup_descriptions, {"AI startup", "Company to test products"})
    
    def test_get_saved_startups_limit(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get("/api/investor/saved-startups?limit=1")

        startup_names = {startup["company_name"] for startup in response.data}
        self.assertSetEqual(startup_names, {"Startup 1"})
        startup_descriptions = {startup["description"] for startup in response.data}
        self.assertSetEqual(startup_descriptions, {"Company to test products"})

    def test_get_saved_startups_order_by_limit(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get("/api/investor/saved-startups?order_by=-created_at&limit=1")

        startup_names = {startup["company_name"] for startup in response.data}
        self.assertSetEqual(startup_names, {"Startup 2"})
        startup_descriptions = {startup["description"] for startup in response.data}
        self.assertSetEqual(startup_descriptions, {"AI startup"})
    
    def test_get_saved_startups_unathorized(self):
        response = self.client.get("/api/investor/saved-startups")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    def test_get_saved_startups_error_token(self):
        self.refresh = RefreshToken.for_user(self.startup1)
        self.access_token = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get("/api/investor/saved-startups")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(response.data['detail'], "User is not linked to an enterprise company.")
    
    def test_get_saved_startups_invalid_query(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get("/api/investor/saved-startups?order_by=unknown_field")
        self.assertEqual(response.status_code, status.HTTP_200_OK)  

        startup_names = {startup["company_name"] for startup in response.data}
        self.assertSetEqual(startup_names, {"Startup 1", "Startup 2"})

        startup_descriptions = {startup["description"] for startup in response.data}
        self.assertSetEqual(startup_descriptions, {"Company to test products", "AI startup"})


        


    
    

    



    