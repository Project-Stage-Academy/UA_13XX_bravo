from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.throttling import AnonRateThrottle
from .utils import generate_verification_token, verify_token
from .serializers import UserSerializer, PasswordResetSerializer, UserCreateSerializer
from users.models import User
from datetime import timedelta



User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    View for registering a new user.

    This view handles the creation of a new user and sends a verification email
    to confirm their email address.
    """

    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def perform_create(self, serializer):
        """
        Save the new user instance and send a verification email.

        Args:
            serializer: The serializer instance containing the user data.

        Returns:
            None
        """
        user = serializer.save(is_active=False)

        token = generate_verification_token(user)
        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email/?token={token}"

        send_mail(
            "Confirm your email",
            f"Click the link to confirm your email: {verification_url}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        

class VerifyEmailView(APIView):
    """
    View for verifying a user's email address.

    This view handles the verification of a user's email address using a token
    sent to their email.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Verify the user's email address using the token from the request.

        Args:
            request: The HTTP request object containing the token.

        Returns:
            Response: A JSON response indicating the result of the verification.
        """
        token = request.GET.get("token")
        user = verify_token(token)

        if not user:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return Response({"message": "Email already verified."}, status=status.HTTP_200_OK)

        user.is_active = True
        user.save()
        return Response({"message": "Email confirmed. You can now log in!"}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    API View to handle password reset requests.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = PasswordResetSerializer  

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.filter(email=email).first()
            if user:
                token = generate_verification_token(user)
                reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/?token={token}"
                email_body = f"Click the link below to reset your password:\n{reset_url}"
                
                send_mail(
                    "Password Reset Request",
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

            return Response({"message": "If an account exists, a reset link has been sent to your email."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    """
    API View to reset password after verifying token.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer  

    def post(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = verify_token(token)
        if not user:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email 
        return token

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer