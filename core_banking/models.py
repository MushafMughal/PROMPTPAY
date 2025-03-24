from django.db import models
from authentication.models import User
import random
import string

class BankAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to User model
    account_number = models.CharField(max_length=16, unique=True)  # 16-digit Pakistani bank account number
    IBAN = models.CharField(max_length=24, unique=True)  # 24-character Pakistani IBAN
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000.00)  # Default balance
    transaction_limit = models.DecimalField(max_digits=12, decimal_places=2, default=50000.00)  # Default limit
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for account creation
    
    def __str__(self):
        return f"{self.user.username} - {self.account_number}"

    @staticmethod
    def generate_unique_account_number():
        """Generates a unique 14-digit account number"""
        while True:
            account_number = ''.join(random.choices(string.digits, k=14))
            if not BankAccount.objects.filter(account_number=account_number).exists():
                return account_number

