from django.urls import path
from .views import RegisterView, VerifyEmailView, LoginView, LogoutView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path("logout/", LogoutView.as_view(), name="logout"),
]