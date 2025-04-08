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

# @api_view(['GET'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
# def userdetails(request):
#     """Retrieve user details"""
#     user = request.user
#     serializer = UserSerializer(user)
#     return Response(serializer.data, status=200)


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
            data = request.data
            user_otp = data.get("otp")

            # Retrieve OTP from cache
            stored_otp = cache.get(f"otp_{user_id}")

            if stored_otp and stored_otp == user_otp:
                cache.delete(f"otp_{user_id}")  # Delete OTP from cache after successful verification
                return Response({"status": True, "data": None, "message": "OTP verified.", "route": "success"}, status=200)
            
            elif stored_otp and stored_otp != user_otp:
                return Response({"status": False, "data": None, "message": "Wrong OTP. Please try again.", "route": "unsuccess"}, status=400)
            
            else:
                return Response({"status": False, "data": None, "message": "Invalid OTP", "route": "unsuccess"}, status=400)
                
        except Exception as e:
            return Response({"status": False, "data": None, "message": f"Error: {str(e)}", "route": "unsuccess"}, status=500)


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
            cache.set(f"otp_{user_id}", new_otp, timeout=300)  # 5 min expiry
            send_user_registration_emails(user_email, new_otp)
        
            return Response({
                            "status": True,
                            "data": None,
                            "message": "OTP has been resent.",
                            "route": "otp_verification"
                        }, status=200)

        except Exception as e:
            return Response({"status": False, "message": f"Error: {str(e)}"}, status=500)