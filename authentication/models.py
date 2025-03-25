from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils.timezone import now, timedelta


# New Model for Blacklisted Access Token
class BlacklistedAccessToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


# New Model for User
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
    

# New Model for Authentication
class Authentication(models.Model):
    auth_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_login_time = models.DateTimeField(null=True, blank=True)
    failed_attempts = models.IntegerField(default=0)
    two_factor_enabled = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)  # Stores lock timestamp

    def __str__(self):
        return f"Auth({self.user.username})"

    def unlock_if_time_passed(self):
        """Unlock user if 15 minutes have passed."""
        if self.is_locked and self.locked_at:
            unlock_time = self.locked_at + timedelta(minutes=15)
            if now() >= unlock_time:  # Unlock if 15 min passed
                self.is_locked = False
                self.failed_attempts = 0
                self.locked_at = None
                self.save()
