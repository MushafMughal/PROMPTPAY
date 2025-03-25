from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import User
from .models import *

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
        )

@receiver(post_save, sender=User)
def create_card(sender, instance, created, **kwargs):
    if created:  # Only create a card when a new user registers
        card_number = Card.generate_unique_card_number()
        expiry_date = Card.generate_expiry_date()
        cvv = Card.generate_unique_cvv()

        Card.objects.create(
            user=instance,
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv,
        )