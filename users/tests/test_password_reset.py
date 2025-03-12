from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()

class PasswordResetSerializerTests(APITestCase):

    def test_valid_email(self):
        user = User.objects.create_user(email="test@example.com", password="TestPassword123")
        response = self.client.post("/auth/password-reset/", {"email": "test@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_invalid_email(self):
        response = self.client.post("/auth/password-reset/", {"email": "fake@example.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        

class PasswordResetIntegrationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="oldpassword")

    def test_full_password_reset_flow(self):
        response = self.client.post("/auth/password-reset/", {"email": self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        from django.contrib.auth.tokens import default_token_generator
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        reset_response = self.client.post(f"/auth/password-reset-confirm/{uid}/{token}/", {
            "uid": uid,
            "token": token,
            "new_password": "newpassword123"
        })
        self.assertEqual(reset_response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))
