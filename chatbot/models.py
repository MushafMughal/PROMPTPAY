from django.db import models

class Transaction(models.Model):
    account_number = models.CharField(max_length=50, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    recipient_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction to {self.recipient_name or 'Unknown'} - {self.amount or 'Unknown'}"
