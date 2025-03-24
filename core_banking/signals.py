from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import User
from .models import BankAccount

@receiver(post_save, sender=User)
def create_bank_account(sender, instance, created, **kwargs):
    if created:  # Only create an account when a new user registers
        account_number = BankAccount.generate_unique_account_number()
        bank_code = "PPAY00"
        iban = f"PK36{bank_code}{account_number}"  # IBAN structure

        BankAccount.objects.create(
            user=instance,
            account_number=account_number,
            IBAN=iban,
            balance=1000.00,  # Default starting balance
            transaction_limit=50000.00  # Default limit
        )
