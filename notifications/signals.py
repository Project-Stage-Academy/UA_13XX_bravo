from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, Type
from companies.models import CompanyFollowers
from django.contrib.auth import get_user_model
from .utils import send_email_notification
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=CompanyFollowers)
def create_notification_for_new_follower(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        notif_type, _ = Type.objects.get_or_create(name="new_follower")
        Notification.objects.create(
            user=instance.investor.user,
            type=notif_type,
            entity=instance.startup,
            content=f"{instance.investor.company_name} started following {instance.startup.company_name}"
        )
        send_email_notification(
            instance.investor.user, "new_follower",
            f"{instance.investor.company_name} started following {instance.startup.company_name}"
        )
    except Exception as e:
        logger.error(f"Error creating new follower notification: {e}")
