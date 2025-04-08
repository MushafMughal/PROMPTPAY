
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from authentication.utils import CustomAPIException

# Get user's bank account details
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    """Get authenticated user's bank account details"""
    try:
        account = BankAccount.objects.get(user=request.user)  # ✅ Fetch data for logged-in user only
        serializer = BankAccountSerializer(account)
        raise CustomAPIException(True, serializer.data, "Account details fetched successfully", 200)
    except BankAccount.DoesNotExist:
        raise CustomAPIException(False, None, "Account details not found", 404)
    

# Get user's card details
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_card_details(request):
    """Get authenticated user's card details"""
    try:
        card = Card.objects.get(user=request.user)  # ✅ Fetch card for logged-in user only
        serializer = CardSerializer(card)
        raise CustomAPIException(True, serializer.data, "Card details fetched successfully", 200)
    except Card.DoesNotExist:
        raise CustomAPIException(False, None, "Card details not found", 404)
    
# Update user's card details
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_card_limit(request):
    """Update the card limit of the authenticated user"""
    try:
        card = Card.objects.get(user=request.user)  # ✅ Fetch user's card
    except Card.DoesNotExist:
        raise CustomAPIException(False, None, "Card details not found", 404)

    new_limit = request.data.get("card_limit")  # ✅ Get new card limit from request

    if new_limit is None:
        raise CustomAPIException(False, None, "Card limit is required", 400)

    try:
        new_limit = float(new_limit)  # Convert to float
        if new_limit <= 0:
            raise CustomAPIException(False, None, "Card limit must be a positive value", 400)
    except ValueError:
        raise CustomAPIException(False, None, "Invalid card limit value", 400)

    card.card_limit = new_limit  # ✅ Update card limit
    card.save()  # ✅ Save changes

    serializer = CardSerializer(card)  # Serialize updated card details
    raise CustomAPIException(True, serializer.data, "Card limit updated successfully", 200)



# Get user's payee details
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_payees(request):
    """Retrieve payees for the authenticated user"""
    payees = Payee.objects.filter(user=request.user)
    serializer = PayeeSerializer(payees, many=True)
    raise CustomAPIException(True, serializer.data, "Payees fetched successfully", 200)

# Add a new payee
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_payee(request):
    """Add a new payee for the authenticated user"""
    serializer = PayeeSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save(user=request.user)
        raise CustomAPIException(True, serializer.data, "Payee added successfully", 201)

    messages = [msg.rstrip('.') for messages in serializer.errors.values() for msg in messages]
    error_messages = " and ".join(messages) + ("." if messages else "")
    raise CustomAPIException(False, None, error_messages, 400)


# Get user's transaction history (List View)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_transactions(request):
    """Retrieve a summary of all transactions for the logged-in user"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_time')
    serializer = TransactionListSerializer(transactions, many=True)
    # return Response(serializer.data, status=200)\
    raise CustomAPIException(True, serializer.data, "Transactions fetched successfully", 200)


# Get full details of a specific transaction (Detail View)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def transaction_details(request, transaction_id):
    """Retrieve full details of a specific transaction"""
    try:
        transaction = get_object_or_404(Transaction, user=request.user, transaction_id=transaction_id)
        serializer = TransactionDetailSerializer(transaction)

        return Response({
            "status": True,
            "data": serializer.data,
            "message": "Transaction details fetched successfully"
        }, status=200)    
    
    except Transaction.DoesNotExist:
        raise CustomAPIException(False, None, "Transaction not found", 404)
    except Exception as e:
        raise CustomAPIException(False, None, str(e), 500)


