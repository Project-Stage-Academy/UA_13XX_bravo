from django.db import models
from users.models import User
from phonenumber_field.modelfields import PhoneNumberField

COMPANY_TYPES = [
    ("startup", "Startup"),
    ("enterprise", "Enterprise"),
    ("nonprofit", "Non-Profit"),
]


class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    startup_logo = models.URLField(blank=True, null=True, default="")
    industry = models.CharField(max_length=255, blank=True, null=True)
    required_funding = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    company_size = models.PositiveIntegerField(blank=True, null=True)  # або models.CharField(...) для категорій
    phone_number = PhoneNumberField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(
    max_length=255, choices=COMPANY_TYPES, blank=True, null=True, default=""
)
    
    def __str__(self):
        return f"{self.company_name} - {self.id}"

    class Meta:
        verbose_name_plural = "Company"


class UserToCompany(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="company_memberships"
    )
    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE, related_name="employees"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.company}"

    class Meta:
        unique_together = ("user", "company")
        verbose_name_plural = "User to Company"
