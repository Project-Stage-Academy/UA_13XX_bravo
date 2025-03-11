from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from .utils import generate_verification_token, verify_token
from .serializers import UserSerializer, UserCreateSerializer 

from users.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email 
        return token

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer