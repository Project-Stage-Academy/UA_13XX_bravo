from django.db import models
from users.models import User

COMPANY_TYPES = [
    ("startup", "Startup"),
    ("enterprise", "Enterprise"),
    ("nonprofit", "Non-Profit"),
]


class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    startup_logo = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(
        max_length=255, choices=COMPANY_TYPES, blank=True, null=True
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


class StartupViewHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="viewed_startups"
    )
    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE, related_name="viewed_by"
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-viewed_at"]  
        unique_together = ("user", "company")  
        verbose_name_plural = "Startup View History"