from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()

class Subscription(models.Model):
    creator = models.ForeignKey(
        User,
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

    def __str__(self):
        return f"Subscription #{self.pk} — ({self.investment_share}%)"