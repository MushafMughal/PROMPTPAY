from rest_framework import serializers
from .models import BankAccount

class BankAccountSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.name", read_only=True)  # Get name

    class Meta:
        model = BankAccount
        fields = ['name', 'account_number', 'balance', 'IBAN', 'transaction_limit']
