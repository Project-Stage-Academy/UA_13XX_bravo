from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, Type
from companies.models import CompanyFollowers
from users.models import User
from .utils import send_email_notification

@receiver(post_save, sender=CompanyFollowers)
def create_notification_for_new_follower(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.investor,  
            type=Type.objects.get(name="new_follower"),
            entity=instance.startup,
            content=f"{instance.investor.username} started following {instance.startup.company_name}"
        )
        send_email_notification(instance.investor, "new_follower", f"{instance.investor.username} started following {instance.startup.company_name}")

# це на випалок якщо потрібно буде меседжі надсилати по чаті використовуючи communications
# @receiver(post_save, sender=Message)
# def create_notification_for_new_message(sender, instance, created, **kwargs):
#     if created:
#         Notification.objects.create(
#             user=instance.recipient,
#             type=Type.objects.get(name="new_message"),
#             entity=instance,
#             content=f"New message from {instance.sender.username}"
#         )
#         send_email_notification(instance.recipient, "new_message", f"New message from {instance.sender.username}")
