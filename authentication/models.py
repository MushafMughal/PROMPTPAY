from django.db import models
from django.contrib.auth.hashers import make_password

class User(models.Model):
    cnic = models.CharField(max_length=15, primary_key=True)  # CNIC as PK
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=256)  # Will be hashed
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)  # Hash the password
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
