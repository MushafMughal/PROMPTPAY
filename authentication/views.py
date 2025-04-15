from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import *
from .serializers import *
from .signals import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.contrib.auth import get_user_model
import json
from .utils import *
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from authentication.utils import generate_otp
from core_banking.models import *
from core_banking.utils import *
from decimal import Decimal
from django.forms.models import model_to_dict



# ✅ Register a new user
class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            raise CustomAPIException(True, None, "User registered successfully!", 201)
        
        messages = [msg.rstrip('.') for messages in serializer.errors.values() for msg in messages]
        error_messages = " and ".join(messages) + ("." if messages else "")

        raise CustomAPIException(False, None, error_messages, 400)


# ✅ List all users (Admin or authorized users can access)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# ✅ Retrieve user details and update (Admin or authorized users can access)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_user_details(request):
    """Update name, email, and phone number for the authenticated user"""
    user = request.user

    name = request.data.get("name")
    email = request.data.get("email")
    phone_number = request.data.get("phone number")

    if not name and not email and not phone_number:
        raise CustomAPIException(False, None, "No data provided to update", 400)

    # ✅ Validate name
    if name:
        if len(name.strip()) == 0:
            raise CustomAPIException(False, None, "Name cannot be empty", 400)
        user.name = name.strip()

    # ✅ Validate email
    if email:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise CustomAPIException(False, None, "Invalid email format", 400)
        user.email = email.strip()

    # ✅ Validate phone number
    if phone_number:
        if not re.match(r"^\+92\d{10}$", phone_number):
            raise CustomAPIException(False, None, "Phone number must be in the format +92xxxxxxxxxx", 400)
        user.phone_number = phone_number.strip()

    user.save()
    serializer = UserSerializer(user)
    raise CustomAPIException(True, serializer.data, "User details updated successfully", 200)


# ✅ Change user password (JWT Protected)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_password(request):
    """Allow authenticated user to change their password"""
    user = request.user

    current_password = request.data.get("current password")
    new_password = request.data.get("new password")
    confirm_password = request.data.get("confirm password")

    # 🔍 Check all fields
    if not current_password or not new_password or not confirm_password:
        raise CustomAPIException(False, None, "All password fields are required", 400)

    # 🔐 Verify current password
    if not check_password(current_password, user.password):
        raise CustomAPIException(False, None, "Current password is incorrect", 401)

    # 🔁 Check new vs confirm
    if new_password != confirm_password:
        raise CustomAPIException(False, None, "New password and confirm password do not match", 400)

    # 🛡 Validate new password
    if len(new_password) < 8:
        raise CustomAPIException(False, None, "Password must be at least 8 characters long", 400)


    # ✅ Update password
    user.password = make_password(new_password)
    user.save()

    raise CustomAPIException(True, None, "Password changed successfully", 200)


# ✅ Login user and get token and trigger Custom signal
User = get_user_model()
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username  # Custom claim
        token["user_id"] = user.id
        return token

    def validate(self, attrs):
        username_or_email_or_cnic = attrs.get("username")
        password = attrs.get("password")

        user = None
        if "@" in username_or_email_or_cnic:
            user = User.objects.filter(email=username_or_email_or_cnic).first()
        elif username_or_email_or_cnic.isdigit():
            user = User.objects.filter(cnic=username_or_email_or_cnic).first()
        else:
            user = User.objects.filter(username=username_or_email_or_cnic).first()

        if not user:
            raise CustomAPIException(False, None, "This User doesn't exist!", 404)
            
        auth_instance, created = Authentication.objects.get_or_create(user=user)

        # ✅ Auto-unlock logic
        auth_instance.unlock_if_time_passed()  

        if auth_instance.is_locked:
            # ❌ Account is locked
            UserActivityLog.objects.create(
                user=user,
                action="login",
                status="failed",
                additional_info=json.dumps({"reason": "Account is locked"}),
            )
            # raise CustomAPIException("Your account is locked. Try again later.", 403)
            raise CustomAPIException(False, None, "Your account is locked. Try again later.", 403)

        if not user.check_password(password):
            # ❌ Failed login attempt -> LOG IT
            ip_address = self.context['request'].META.get('REMOTE_ADDR', 'Unknown IP')
            user_agent = self.context['request'].META.get('HTTP_USER_AGENT', 'Unknown User Agent')
            UserActivityLog.objects.create(
                user=user,
                action="login",
                ip_address=ip_address,
                status="failed",
                user_agent=user_agent,
                additional_info=json.dumps({"reason": "Invalid Password"})
            )
            auth_instance.failed_attempts += 1
            if auth_instance.failed_attempts >= 5:
                auth_instance.is_locked = True
                auth_instance.locked_at = now()  # Set lock time
            auth_instance.save()
            raise CustomAPIException(False, None, "Invalid Password", 401)

        # ✅ Fire the custom signal manually after successful authentication
        custom_user_logged_in.send(sender=self.__class__, request=self.context['request'], user=user)

        data = super().validate({"username": user.username, "password": password})
        data["username"] = user.username
        data["user_id"] = user.id
        
        # Log the successful login event
        ip_address = self.context['request'].META.get('REMOTE_ADDR', 'Unknown IP')
        user_agent = self.context['request'].META.get('HTTP_USER_AGENT', 'Unknown User Agent')
        UserActivityLog.objects.create(
            user=user,
            action="login",
            ip_address=ip_address,
            status="success",
            user_agent=user_agent,
            additional_info=json.dumps({"status": "Successful login"})
        )
        
        raise CustomAPIException(True, data, "Login successful!", 200)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# ✅ Logout user and blacklist refresh token
class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        refresh_token = request.data.get("refresh")
        access_token = request.auth  # Get access token from request header
        user = request.user
        ip_address = request.META.get('REMOTE_ADDR', 'Unknown IP')
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown User Agent')

        # ✅ Blacklist Refresh Token
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                return Response({"error": "Invalid or already blacklisted refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ Blacklist Access Token (custom method)
        if access_token:
            token_str = str(access_token)
            # Avoid duplicate entries
            if not BlacklistedAccessToken.objects.filter(token=token_str).exists():
                BlacklistedAccessToken.objects.create(token=token_str)

            # ✅ Remove from cache immediately
            cache.set(f"blacklisted_{token_str}", True, timeout=3600)

            # ✅ Log the successful logout in UserActivityLog
            UserActivityLog.objects.create(
                user=user,
                action="logout",
                status="success",
                timestamp=now(),
                ip_address=ip_address,
                user_agent=user_agent,
                additional_info={"message": "successfully logged out"},
            )
            # return Response({"message": "Logged out successfully!"}, status=status.HTTP_205_RESET_CONTENT)
            raise CustomAPIException(True, None, "Logged out successfully!", 205)

        else:
            # return Response({"error": "Access token is required"}, status=status.HTTP_400_BAD_REQUEST)
            raise CustomAPIException(False, None, "Access token is required", 400)
    

class VerifyOTPAPI(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to verify OTP (JWT Protected)"""
        try:

            user_id = request.user.id  # Get user ID from JWT
            user = request.user
            data = request.data
            user_otp = data.get("otp")

            # Retrieve OTP from cache
            stored_otp = cache.get(f"otp_{user_id}")

            if stored_otp and stored_otp == user_otp:
                cache.delete(f"otp_{user_id}")  # Delete OTP from cache after successful verification

                recipient_account_number = data.get("account_number")
                amount = data.get("amount")
                amount = Decimal(str(amount))
                cleaned_account_number = recipient_account_number.replace(" ", "")
                recipient_account = BankAccount.objects.get(account_number=cleaned_account_number)
                sender_account = BankAccount.objects.get(user=user)
                  

                # 🔐 Optional: add service fee logic here if needed
                service_fee = Decimal("0.00")
                total_amount = amount + service_fee

                # 🔄 Update balances
                sender_account.balance -= total_amount
                recipient_account.balance += amount
                sender_account.save()
                recipient_account.save()
                tx_id = generate_unique_transaction_id()


                # 🧾 Log debit (sender)
                Transaction.objects.create(
                    user=user,
                    transaction_id=tx_id,
                    stan=generate_unique_stan(),
                    rrn=generate_unique_rrn(),
                    transaction_type="debit",
                    amount=amount,
                    service_fee=service_fee,
                    total_amount=total_amount,
                    source_account_title=user.name,
                    source_bank=sender_account.bank_name,
                    source_account_number=sender_account.account_number,
                    destination_account_title=recipient_account.user.name,
                    destination_bank=recipient_account.bank_name,
                    destination_account_number=recipient_account.account_number,
                    channel="Raast"
                )

                # 🧾 Log credit (recipient)
                Transaction.objects.create(
                    user=recipient_account.user,
                    transaction_id=tx_id,
                    stan=generate_unique_stan(),
                    rrn=generate_unique_rrn(),
                    transaction_type="credit",
                    amount=amount,
                    service_fee=Decimal("0.00"),
                    total_amount=amount,
                    source_account_title=user.name,
                    source_bank=sender_account.bank_name,
                    source_account_number=sender_account.account_number,
                    destination_account_title=recipient_account.user.name,
                    destination_bank=recipient_account.bank_name,
                    destination_account_number=recipient_account.account_number,
                    channel="Raast"
                )

                return Response({"status": True, "data": None, "message": "OTP verified. Transaction Succesfull"}, status=200)
            
            elif stored_otp and stored_otp != user_otp:
                return Response({"status": False, "data": None, "message": "Wrong OTP. Please try again."}, status=400)
            
            else:
                return Response({"status": False, "data": None, "message": "Invalid OTP"}, status=400)
                
        except Exception as e:
            return Response({"status": False, "data": None, "message": f"Error: {str(e)}"}, status=500)


class ResendOTPAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to resend OTP (JWT Protected)"""
        try:

            user_id = request.user.id
            user = User.objects.get(id=user_id)
            user_email = user.email

            new_otp = generate_otp()
            cache.delete(f"otp_{user_id}")
            cache.set(f"otp_{user_id}", new_otp, timeout=300)  # 5 min expiry
            send_user_registration_emails("mushafmughal12@gmail.com", new_otp)
        
            return Response({
                            "status": True,
                            "data": new_otp,
                            "message": "OTP has been resent.",
                        }, status=200)

        except Exception as e:
            return Response({"status": False, "message": f"Error: {str(e)}"}, status=500)