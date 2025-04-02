import uuid
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from users.managers import UserManager

class UserRole(models.Model):
    INVESTOR = "investor"
    ENTERPRISE = "enterprise"
    STARTUP = "startup"

    ROLE_CHOICES = [
        (INVESTOR, "Investor"),
        (ENTERPRISE, "Enterprise"),
        (STARTUP, "Startup")
    ]
    
    name = models.CharField(max_length=255, choices=ROLE_CHOICES, unique=True)
    
    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list[str] = []

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255, blank=True, default='')
    phone = PhoneNumberField(blank=True, default='')

    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True)
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        db_table = 'users'

    def clean(self):
        if not self.email:
            raise ValueError('Users must have an email address.')
        
        self.email = self.__class__.objects.normalize_email(self.email)
