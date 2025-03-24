
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
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
