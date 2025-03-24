from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser


class BlacklistedAccessToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

class User(AbstractUser):
    name = models.CharField(max_length=255)  # Full Name
    username = models.CharField(max_length=100, unique=True)  # Username (separate from name)
    cnic = models.CharField(max_length=15, unique=True)  # CNIC as Unique Field
    email = models.EmailField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    dob = models.DateField(null=True, blank=True)  # Date of Birth
    password = models.CharField(max_length=256)  # Will be hashed
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)  # Hash the password
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
