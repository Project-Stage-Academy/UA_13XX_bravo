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

def send_notification_and_email(user, notif_type_name, content):
    """
    Creates a notification and sends an email to the user.
    
    :param user: User who will receive the notification
    :param notif_type_name: Name of the notification type (e.g., "new_follower", "new_post")
    :param content: Notification message content
    """
    try:
        notif_type, _ = Type.objects.get_or_create(name=notif_type_name)
        
        Notification.objects.create(
            user=user,
            type=notif_type,
            content=content
        )

        send_mail(
            subject=f"Notification: {notif_type_name}",
            message=content,
            from_email=os.getenv("DEFAULT_FROM_EMAIL"),
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Error creating {notif_type_name} notification: {e}")

# @receiver(post_save, sender=CompanyFollowers)
# def create_notification_for_new_follower(sender, instance, created, **kwargs):
#     if not created:
#         return
    
#     content = f"{instance.investor.company_name} started following {instance.startup.company_name}"
#     send_notification_and_email(investor_user, "new_follower", content) # need to update logic for connecting to the user  (use CompanyFollowers model)


@receiver(post_save, sender=CompanyProfile)
def notify_followers_on_update(sender, instance, created, **kwargs):
    if created:
        return
    
    followers = CompanyFollowers.objects.filter(startup=instance)
    for follow in followers:
        investor_user = UserToCompany.objects.filter(company=follow.investor).first()
        if investor_user:
            content = f"{instance.company_name} updated their profile."
            send_notification_and_email(investor_user.user, "new_post", content)
            print(send_notification_and_email)