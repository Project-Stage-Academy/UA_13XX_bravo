from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from projects.models import Startup  #Startup  потрібно НЕ ЗАБУТИ!!! замінити на відповідне поле коли в апці projects буде створено моделі

@receiver(post_save, sender=Startup)
def create_notification_for_new_follower(sender, instance, created, **kwargs):
    if created:
        
        for follower in instance.followers.all():
            Notification.objects.create(
                user=follower,
                type=Type.objects.get(name="new_follower"),
                entity=instance,
                content=f"{follower.username} started following {instance.name}"
            )

@receiver(post_save, sender=Message)  
def create_notification_for_new_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.recipient,
            type=Type.objects.get(name="new_message"),
            entity=instance,
            content=f"New message from {instance.sender.username}"
        )
