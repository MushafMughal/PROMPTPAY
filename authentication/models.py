from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils.timezone import now, timedelta
from django.core.exceptions import ValidationError


# New Model for Blacklisted Access Token
class BlacklistedAccessToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


# New Model for User
class User(AbstractUser):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=100, unique=True)
    cnic = models.CharField(max_length=15)
    email = models.EmailField(max_length=50, unique=False)
    phone_number = models.CharField(max_length=15, unique=False)
    dob = models.DateField(null=True, blank=True)
    password = models.CharField(max_length=256)
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    

# New Model for Authentication
class Authentication(models.Model):
    auth_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_login_time =  models.DateTimeField(null=True, blank=True)  # Stores last login time
    failed_attempts = models.IntegerField(default=0)
    two_factor_enabled = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)  # Stores lock timestamp

    def __str__(self):
        return f"Auth({self.user.username})"

    def unlock_if_time_passed(self):
        """Unlock user if 15 minutes have passed."""
        if self.is_locked and self.locked_at:
            unlock_time = self.locked_at + timedelta(minutes=2)
            if now() >= unlock_time:  # Unlock if 15 min passed
                self.is_locked = False
                self.failed_attempts = 0
                self.locked_at = None
                self.save()

# New Model for User Activity Log
class UserActivityLog(models.Model):
    ACTION_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('transaction', 'Transaction'),
        ('bill_payment', 'Bill Payment'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
        ('password_forget', 'Password Forget'),
        ('payee_added', 'Payee Added'),
    ]

    STATUS_TYPES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    log_id = models.AutoField(primary_key=True)  # Unique ID for each log entry
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")  # Tracks which user performed the action
    action = models.CharField(max_length=50, choices=ACTION_TYPES)  # What action was performed
    status = models.CharField(max_length=10, choices=STATUS_TYPES, default="success")  # Success or failure
    timestamp = models.DateTimeField(auto_now_add=True)  # When the action was performed
    ip_address = models.GenericIPAddressField()  # Captures the IP address
    user_agent = models.TextField(blank=True, null=True)  # Captures browser, device info
    additional_info = models.JSONField(blank=True, null=True)  # Stores extra details dynamically

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.status} - {self.timestamp}"

