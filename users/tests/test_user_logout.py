from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

User = get_user_model()

class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="oldpassword")
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)
        self.access = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_logout_success(self):
        response = self.client.post("/auth/logout/", {"refresh_token": str(self.refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Successfully logged out.")

    def test_logout_invalid_token(self):
        response = self.client.post("/auth/logout/", {"refresh_token": "invalid_token"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_logout_missing_token(self):
        response = self.client.post("/auth/logout/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh_token", response.data)  

    def test_logout_unauthorized(self):
        self.client.credentials()  
        response = self.client.post("/auth/logout/", {"refresh_token": str(self.refresh)})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    

        