from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import User
from .models import *
from datetime import timedelta, date


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


@receiver(post_save, sender=User)
def create_default_bills(sender, instance, created, **kwargs):
    if created:
        today = date.today()
        default_bills = [
            {
                "bill_type": "electricity",
                "company": "K-Electric",
                "consumer_number": "12345678901",  # Typically 11-digit number
                "amount": 1000.00,
                "due_date": today + timedelta(days=7),
                "payment_status": False,
            },
            {
                "bill_type": "gas",
                "company": "SSGC",
                "consumer_number": "1234567890-1",  # 10-digit + check digit format
                "amount": 1000.00,
                "due_date": today + timedelta(days=30),
                "payment_status": False,
            },
            {
                "bill_type": "water",
                "company": "KW&SB",
                "consumer_number": "WTR-09876543",  # Prefix style used in older systems
                "amount": 1000.00,
                "due_date": today + timedelta(days=30),
                "payment_status": False,
            },
            {
                "bill_type": "internet",
                "company": "PTCL",
                "consumer_number": "021-38294756",  # City code + phone format for PTCL landline/broadband
                "amount": 1000.00,
                "due_date": today + timedelta(days=14),
                "payment_status": False,
            },
        ]

        for bill in default_bills:
            Bill.objects.create(
                user=instance,
                bill_type=bill["bill_type"],
                company=bill["company"],
                consumer_number=bill["consumer_number"],
                amount=bill["amount"],
                payment_status=bill["payment_status"],
                due_date=bill["due_date"],
            )




