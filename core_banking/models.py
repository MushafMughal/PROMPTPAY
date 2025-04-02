from django.db import models
from authentication.models import User
import random
import string
import datetime

# User's bank account details
class BankAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to User model
    account_number = models.CharField(max_length=14, unique=True)  # 16-digit Pakistani bank account number
    IBAN = models.CharField(max_length=24, unique=True)  # 24-character Pakistani IBAN
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)  # Default balance
    bank_name = models.CharField(max_length=255, default="PromptPay")  # Default bank name
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for account creation
    last_updated = models.DateTimeField(auto_now=True)  # Timestamp for last update

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
    expiry_date = models.CharField(max_length=5)  # Format MM/YY
    cvv = models.CharField(max_length=3)
    card_type = models.CharField(max_length=20, default='Visa')
    card_limit = models.DecimalField(max_digits=10, decimal_places=2, default=50000.00)  # Default limit
    
    def __str__(self):
        return f"{self.user.username} - **** **** **** {self.card_number[-4:]}"  # Masked for security

    @staticmethod
    def luhn_checksum(card_number):
        """Calculates the Luhn checksum for a given card number"""
        digits = [int(d) for d in card_number]
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        return sum(digits) % 10

    @staticmethod
    def generate_unique_card_number():
        """Generates a unique 16-digit Visa card number"""
        while True:
            card_number = "4" + ''.join(random.choices("0123456789", k=14))  # Start with 4
            
            # Calculate and append Luhn checksum
            checksum_digit = (10 - Card.luhn_checksum(card_number + "0")) % 10
            card_number += str(checksum_digit)

            # Ensure uniqueness
            if not Card.objects.filter(card_number=card_number).exists():
                return card_number

    @staticmethod
    def generate_expiry_date():
        """Generates a valid expiry date (MM/YY) at least 3 years from now"""
        today = datetime.date.today()
        expiry_year = today.year + 5  # Add 3 years
        expiry_month = today.month
        return f"{expiry_month:02d}/{str(expiry_year)[-2:]}"  # MM/YY format

    @staticmethod
    def generate_unique_cvv():
        """Generates a unique 3-digit CVV"""
        while True:
            cvv = random.randint(100, 999)
            if not Card.objects.filter(cvv=cvv).exists():
                return cvv


#Users Payee details  
class Payee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payees")  # User can have multiple payees
    payee_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when payee was added

    def __str__(self):
        return f"{self.user.username} -> {self.payee_name} ({self.bank_name})"


#Transaction details
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),  # Money received
        ('debit', 'Debit'),  # Money sent
        ('bill_payment', 'Bill Payment'),  # Paying a bill
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")  # User who owns the transaction
    transaction_id = models.CharField(max_length=50, unique=True)  # Unique transaction identifier
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)  # Type of transaction
    transaction_time = models.DateTimeField(auto_now_add=True)  # Timestamp

    # Amount details
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Transaction amount
    service_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Service fee
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)  # Total amount including fee

    # Account details (common for all transactions)
    source_account_title = models.CharField(max_length=255)  # Sender name (for received transactions) or User (for sent)
    source_bank = models.CharField(max_length=255, blank=True, null=True)  # Optional for bill payments
    source_account_number = models.CharField(max_length=20, blank=True, null=True)  # Masked account number

    destination_account_title = models.CharField(max_length=255)  # Receiver name or biller name
    destination_bank = models.CharField(max_length=255, blank=True, null=True)  # Optional for bill payments
    destination_account_number = models.CharField(max_length=20, blank=True, null=True)  # Masked account number

    # Bill Payment Specific Fields
    consumer_name = models.CharField(max_length=255, blank=True, null=True)  # For bill payments
    consumer_number = models.CharField(max_length=20, blank=True, null=True)  # For bill payments

    channel = models.CharField(max_length=50)  # e.g., Raast, IBFT

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - Rs. {self.amount}"
