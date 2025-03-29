from django.db import models

from companies.models import CompanyProfile


PROJECT_STATUSES = [
    ("active", "Active"),
    ("completed", "Completed"),
]

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(choices=PROJECT_STATUSES, blank=False)
    information = models.TextField()
    required_funding = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)
    raised_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'project'