from django.db import models

from companies.models import CompanyProfile
from decimal import Decimal
from django.core.exceptions import ValidationError


class ProjectStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=ProjectStatus.choices)
    information = models.TextField()
    required_funding = models.DecimalField(
        max_digits=15, decimal_places=2, blank=False, null=False
    )
    raised_amount = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=False, default=Decimal("0.00")
    )

    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE, related_name="projects"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.raised_amount and self.raised_amount > self.required_funding:
            raise ValidationError("Raised amount cannot exceed required funding.")

    class Meta:
        db_table = "project"
