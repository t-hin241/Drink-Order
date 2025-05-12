from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='users/', blank=True, null=True)
    # Add role-specific fields
    is_customer = models.BooleanField(default=True)
    is_bartender = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    share_profile = models.BooleanField(default=True, help_text="Allow bartenders to view your profile (e.g., favorite drinks, visit frequency).")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"