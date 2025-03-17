from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification, NotificationPreference, Type
from .serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    TypeSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Notification.objects.filter(user=self.request.user)
            .select_related("entity", "type")
            .order_by("-created_at")
        )

    @action(detail=True, methods=["patch"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({"status": "marked as read"})

    @action(detail=False, methods=["patch"])
    def mark_all_as_read(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        count = notifications.update(is_read=True)
        return Response({"status": f"{count} notifications marked as read"})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.id)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating notification preference for user {request.user.id}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        type_name = serializer.validated_data.get("type")
        type_instance = Type.objects.filter(name=type_name).first()

        if not type_instance:
            raise ValidationError(f"Type '{type_name}' not found.")

        duplicate_exists = NotificationPreference.objects.filter(
            user=request.user, type=type_instance
        ).exists()

        if duplicate_exists:
            raise ValidationError(
                "A preference with this user and type already exists.[view]"
            )

        serializer.save(user=request.user, type=type_instance)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TypesListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        types = Type.get_cached_types()
        serializer = TypeSerializer(types, many=True)
        return Response(serializer.data)
