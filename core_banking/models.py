from django.db import models
from authentication.models import User
import random
import string
from datetime import timedelta, date


# User's bank account details
class BankAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to User model
    account_number = models.CharField(max_length=16, unique=True)  # 16-digit Pakistani bank account number
    IBAN = models.CharField(max_length=24, unique=True)  # 24-character Pakistani IBAN
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)  # Default balance
    bank_name = models.CharField(max_length=255, default="PromptPay")  # Default bank name
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


# User's card details
class Card(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each user gets one card
    card_number = models.CharField(max_length=16, unique=True)
    expiry_date = models.CharField(max_length=7)  # Format YYYY/MM
    cvv = models.CharField(max_length=3)
    card_type = models.CharField(max_length=20, default='Visa')
    card_limit = models.DecimalField(max_digits=10, decimal_places=2, default=50000.00)  # Default limit
       
    def __str__(self):
        return f"{self.user.username} - **** **** **** {self.card_number[-4:]}"  # Masked for security

    @staticmethod
    def generate_unique_card_number():
        """Generates a unique 16-digit card number"""
        while True:
            card_number = ''.join(random.choices(string.digits, k=16))
            if not Card.objects.filter(card_number=card_number).exists():
                return card_number
            
    @staticmethod
    def generate_unique_cvv():
        """Generates a unique 3-digit CVV"""
        while True:
            cvv = random.randint(100, 999)
            if not Card.objects.filter(cvv=cvv).exists():
                return cvv
