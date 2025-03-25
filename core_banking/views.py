
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *


# Get user's bank account details
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    """Get authenticated user's bank account details"""
    try:
        account = BankAccount.objects.get(user=request.user)  # ✅ Fetch data for logged-in user only
        serializer = BankAccountSerializer(account)
        return Response(serializer.data, status=200)
    except BankAccount.DoesNotExist:
        return Response({"error": "User account not found"}, status=404)


# Get user's card details
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_card_details(request):
    """Get authenticated user's card details"""
    try:
        card = Card.objects.get(user=request.user)  # ✅ Fetch card for logged-in user only
        serializer = CardSerializer(card)
        return Response(serializer.data, status=200)
    except Card.DoesNotExist:
        return Response({"error": "Card not found"}, status=404)


# Get user's payee details
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def manage_payees(request):
    """Retrieve or add payees for the authenticated user"""
    if request.method == 'GET':
        payees = Payee.objects.filter(user=request.user)
        serializer = PayeeSerializer(payees, many=True)
        return Response(serializer.data, status=200)

    elif request.method == 'POST':
        serializer = PayeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # ✅ Automatically associate the logged-in user
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Get user's transaction history (List View)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_transactions(request):
    """Retrieve a summary of all transactions for the logged-in user"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_time')
    serializer = TransactionListSerializer(transactions, many=True)
    return Response(serializer.data, status=200)


# Get full details of a specific transaction (Detail View)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def transaction_details(request, transaction_id):
    """Retrieve full details of a specific transaction"""
    transaction = get_object_or_404(Transaction, user=request.user, transaction_id=transaction_id)
    serializer = TransactionDetailSerializer(transaction)
    return Response(serializer.data, status=200)


