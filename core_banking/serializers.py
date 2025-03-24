from rest_framework import serializers
from .models import *

# Serializer for BankAccount model
class BankAccountSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.name", read_only=True)  # Get name
    email = serializers.EmailField(source="user.email", read_only=True)  # Get email
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)  # Get phone number

    class Meta:
        model = BankAccount
        fields = ['name', 'email', 'phone_number','bank_name', 'account_number', 'balance', 'IBAN']


# Serializer for Card model
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'  # Includes all fields in API response
