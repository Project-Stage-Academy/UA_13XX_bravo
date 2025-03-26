from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, Type
from companies.models import CompanyFollowers, CompanyProfile, UserToCompany
from django.contrib.auth import get_user_model
from .utils import send_email_notification
from django.core.mail import send_mail
import os
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

@receiver(post_save, sender=CompanyProfile)
def notify_followers_on_update(sender, instance, created, **kwargs):
    if created:
        return
    
    try:
        notification_type, _ = Type.objects.get_or_create(name="new_post")
        followers = CompanyFollowers.objects.filter(startup=instance)
        for follow in followers:
            investor_user = UserToCompany.objects.filter(company=follow.investor).first()

            Notification.objects.create(
                user=investor_user.user,
                type=notification_type,
                content=f"{instance.company_name} updated their profile."
            )
            send_mail(
                    subject="Notification: new_post",
                    message=f"{instance.company_name} updated their profile.",
                    from_email=os.getenv("DEFAULT_FROM_EMAIL"),
                    recipient_list=[investor_user.user.email],
                    fail_silently=False,
                )
            
    except Exception as e:
        logger.error(f"Error creating update notification: {e}")
        print(e)