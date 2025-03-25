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


# Serializer for Payee model
class PayeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payee
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}  # ✅ User field is read-only

    def validate_account_number(self, value):
        """Ensure account number is exactly 14 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("Account number must contain only digits.")
        if len(value) != 14:
            raise serializers.ValidationError("Account number must be exactly 14 digits.")
        return value


# Serializer for transaction list view (Screen 1)
class TransactionListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['transaction_id', 'name', 'transaction_type', 'amount']

    def get_name(self, obj):
        """Returns the correct name depending on the transaction type"""
        return obj.destination_account_title if obj.transaction_type in ["debit", "bill_payment", "subscription"] else obj.source_account_title

# Serializer for Transaction model
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}  # User auto-assigned

# Serializer for transaction detail view (Screen 2)
class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'transaction_id', 'transaction_time', 'transaction_type', 
            'amount', 'service_fee', 'total_amount', 
            'source_account_title', 'source_bank', 'source_account_number',
            'destination_account_title', 'destination_bank', 'destination_account_number',
            'channel', 'consumer_name', 'consumer_number'
        ]

