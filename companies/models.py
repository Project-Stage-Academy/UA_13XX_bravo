from django.db import models
from users.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError


class CompanyType:
    STARTUP = "startup"
    ENTERPRISE = "enterprise"
    NONPROFIT = "nonprofit"

    CHOICES = [
        (STARTUP, "Startup"),
        (ENTERPRISE, "Enterprise"),
        (NONPROFIT, "Non-Profit"),
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
      max_length=255, choices=CompanyType.CHOICES, blank=True, null=True
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
        """Ensure that investor is an enterprise and startup is a startup."""
        errors = {}
        
        if self.investor.type != CompanyType.ENTERPRISE:
            errors["investor"] = "The company must be an investor (enterprise)."
            
        if self.startup.type != CompanyType.STARTUP:
            errors["startup"] = "The company must be a startup."
            
        if self.investor == self.startup:
            errors["non_self_follow"] = "A company cannot follow itself."
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        try:
            self.clean()
        except ValidationError:
            raise 
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.investor.company_name} follows {self.startup.company_name}"
