from rest_framework import viewsets, permissions
from .models import Subscription
from .serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для перегляду і створення інвестицій користувача.
    Інші дії, такі як оновлення та видалення, заборонені.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(creator=self.request.user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_permissions(self):
        if self.action in ["list", "create", "retrieve"]:
            return super().get_permissions()
        return [permissions.IsAdminUser()]  # updates/deletions are prohibited