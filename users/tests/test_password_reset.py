from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from datetime import datetime, timedelta
from users.utils import generate_verification_token
User = get_user_model()

class PasswordResetIntegrationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="oldpassword")

    def test_invalid_email(self):
        response = self.client.post("/auth/password-reset/", {"email": "fake@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"], 
            "If an account exists, a reset link has been sent to your email."
        )

    def test_weak_password_rejected(self):
        weak_password = "12345678"
        token = generate_verification_token(self.user)

        response = self.client.post(f"/auth/password-reset-confirm/?token={token}", {
            "new_password": weak_password,
            "confirm_password": weak_password
        })
        
        print(response.data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertIn("This password is too common.", response.data["new_password"])
        self.assertIn("This password is entirely numeric.", response.data["new_password"])

    def test_expired_token_rejected(self):

        token = default_token_generator.make_token(self.user)

        self.user.set_password("newpassword123")
        self.user.save()
        
        response = self.client.post(f"/auth/password-reset-confirm/?token={token}", {
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Invalid or expired token.")

    def test_mismatched_passwords_rejected(self):
        token = generate_verification_token(self.user)

        response = self.client.post(f"/auth/password-reset-confirm/?token={token}", {
            "new_password": "newpassword123",
            "confirm_password": "differentpassword"
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)
        self.assertEqual(response.data["new_password"], ["Passwords do not match."])