# companies/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CompanyProfile, StartupViewHistory
from django.utils import timezone

@receiver(post_save, sender=CompanyProfile)
def record_view_history(sender, instance, created, **kwargs):
    """
    This signal is triggered after a CompanyProfile is retrieved,
    automatically recording the view in the StartupViewHistory.
    """
    if not created:
        # This ensures the signal is only triggered when the profile is "retrieved" or updated, not when created
        user = instance.request.user  # Assuming you have a way to pass the user information
        if user:
            # Record the view in the StartupViewHistory
            StartupViewHistory.objects.update_or_create(
                user=user,
                company=instance,
                defaults={"viewed_at": timezone.now()},
            )