from django.db import models
from users.models import User
from django.core.exceptions import ValidationError

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
        return self.company_name

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
        
class CompanyFollowers(models.Model):
    investor = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE, related_name="invested_startups",
    )
    startup = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE, related_name="startup_investors",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("investor", "startup")  
        verbose_name_plural = "Investor-Startup Relations"

    def clean(self):
        if self.investor.type != "enterprise":
            raise ValidationError({"investor": "The company must be an investor (enterprise)."})
        if self.startup.type != "startup":
            raise ValidationError({"startup": "The company must be a startup."})
        if self.investor == self.startup:
            raise ValidationError("A company cannot follow itself.")
    
    def save(self, *args, **kwargs):
        try:
            self.clean()
        except ValidationError as e:
            raise ValidationError(f"Validation Error: {e}")
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.investor.company_name} follows {self.startup.company_name}"
