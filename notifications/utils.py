from django.core.mail import send_mail
from .models import NotificationPreference
import os
import logging

logger = logging.getLogger(__name__)


EMAIL_NOTIFICATION_TYPES = {"new_follow", "new_message", "new_report"}


def send_email_notification(user, event_type, message):
    """
    Check user notification preferences before sending an email.
    """
    try:
        # Check if the event type is in allowed email types and enabled in user preferences
        if (
            event_type in EMAIL_NOTIFICATION_TYPES
            and NotificationPreference.objects.filter(
                user=user, type__name=event_type, enabled=True
            ).exists()
        ):
            send_mail(
                subject=f"Notification: {event_type}",
                message=message,
                from_email=os.getenv("DEFAULT_FROM_EMAIL"),
                recipient_list=[user.email],
                fail_silently=False,
                auth_user=os.getenv("EMAIL_HOST_USER"),
                auth_password=os.getenv("EMAIL_HOST_PASSWORD"),
                connection=None,  # Uses default email backend
            )
    except Exception as e:
        logging.error(f"Email notification failed: {e}")
