from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.contrib.auth import get_user_model
from projects.models import Project
from django.core.exceptions import ValidationError
from django.db.models import Sum as AggregateSum

User = get_user_model()

class Subscription(models.Model):
    """
    Represents an investment made by a user in a specific project.
    """
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    project = models.ForeignKey(
    Project,
    on_delete=models.CASCADE,
    related_name="subscriptions"
    )
    investment_share = models.DecimalField(
        max_digits=5,           # e.g., allows 100.00
        decimal_places=2,       # e.g., 25.50%
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("100.00"))
        ],
        help_text="Percentage of total investment (e.g., 25.50 for 25.5%)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.project:
            total_share = (
                Subscription.objects
                .filter(project=self.project)
                .exclude(pk=self.pk)
                .aggregate(total=Sum("investment_share"))["total"] or 0
            )
            if total_share + self.investment_share > 100:
                raise ValidationError("Total investment for this project cannot exceed 100%.")

    def save(self, *args, **kwargs):
        self.full_clean()  # ensure clean() is called
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Subscription #{self.pk} — ({self.investment_share}%)"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["creator", "project"],
                name="unique_subscription_per_project"
            )
        ]