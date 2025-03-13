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

    def test_weak_password_rejected(self):
        weak_password = "12345678"
        token = generate_verification_token(self.user)

        response = self.client.post(f"/auth/password-reset-confirm/?token={token}", {
            "new_password": weak_password,
            "confirm_password": weak_password
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertTrue(any("password" in err for err in response.data["non_field_errors"]))


    def test_expired_token_rejected(self):
        from datetime import datetime, timedelta
        self.user.last_login = datetime.now() - timedelta(hours=2)
        self.user.save()

        token = default_token_generator.make_token(self.user)

        response = self.client.post(f"/auth/password-reset-confirm/?token={token}", {
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
