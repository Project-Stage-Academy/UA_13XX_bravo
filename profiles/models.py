from django.db import models
from users.models import User


class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    website = models.URLField(blank=True, null=True)
    startup_logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name_plural = "Company"


class UserToCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.company}"

    class Meta:
        verbose_name_plural = "User to Company"
