from django.urls import path
from .views import RegisterView, VerifyEmailView, PasswordResetConfirmView, PasswordResetRequestView, LoginView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
]