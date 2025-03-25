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
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.contrib.auth import get_user_model
import json
from .utils import CustomAPIException


# ✅ Register a new user
class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ List all users (Admin or authorized users can access)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ✅ Retrieve, Update, and Delete a user by CNIC
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'cnic'  # Use CNIC as lookup field


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
            raise CustomAPIException("User not found", 404)
            
        auth_instance, created = Authentication.objects.get_or_create(user=user)

        # ✅ Auto-unlock logic
        auth_instance.unlock_if_time_passed()  

        if auth_instance.is_locked:
            # raise AuthenticationFailed("Your account is locked. Try again later.")
            raise CustomAPIException("Your account is locked. Try again later.", 403)

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
                additional_info=json.dumps({"reason": "Invalid credentials"})
            )
            auth_instance.failed_attempts += 1
            if auth_instance.failed_attempts >= 5:
                auth_instance.is_locked = True
                auth_instance.locked_at = now()  # Set lock time
            auth_instance.save()
            # raise AuthenticationFailed("Invalid credentials")
            raise CustomAPIException("Invalid Password", 401)

        # ✅ Fire the custom signal manually after successful authentication
        custom_user_logged_in.send(sender=self.__class__, request=self.context['request'], user=user)
        # auth_instance.failed_attempts = 0
        # auth_instance.is_locked = False
        # auth_instance.locked_at = None
        # auth_instance.save()

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
        
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# ✅ Logout user and blacklist refresh token
class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user  # Get the logged-in user
        ip_address = request.META.get("REMOTE_ADDR")  # Get user's IP address
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown User Agent")  # Get user's device info

        refresh_token = request.data.get("refresh")
        access_token = request.auth  # Get access token from request header

        if not refresh_token and not access_token:
            # ❌ No tokens provided
            UserActivityLog.objects.create(
                user=user,
                action="logout",
                status="failed",
                timestamp=now(),
                ip_address=ip_address,
                user_agent=user_agent,
                additional_info={"message": "No tokens provided. Please provide a refresh or access token."},
            )
            return Response({"error": "No tokens provided. Please provide a refresh or access token."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # ✅ Blacklist Refresh Token
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    # ❌ Invalid refresh token
                    UserActivityLog.objects.create(
                        user=user,
                        action="logout",
                        status="failed",
                        timestamp=now(),
                        ip_address=ip_address,
                        user_agent=user_agent,
                        additional_info={"message": "Invalid refresh token or it has already been blacklisted."},
                    )
                    return Response({"error": "Invalid refresh token or it has already been blacklisted."}, status=status.HTTP_400_BAD_REQUEST)
            
            # ✅ Blacklist Access Token (custom method)
            if access_token:
                token_str = str(access_token)
                if BlacklistedAccessToken.objects.filter(token=token_str).exists():
                    # ❌ Access token is already blacklisted
                    UserActivityLog.objects.create(
                        user=user,
                        action="logout",
                        status="failed",
                        timestamp=now(),
                        ip_address=ip_address,
                        user_agent=user_agent,
                        additional_info={"message": "Access token is already blacklisted."},
                    )
                    return Response({"error": "Access token is already blacklisted."}, status=status.HTTP_400_BAD_REQUEST)
                
                BlacklistedAccessToken.objects.create(token=token_str)
                cache.set(f"blacklisted_{token_str}", True, timeout=3600)  # ✅ Remove from cache immediately
            
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

            return Response({"message": "Logged out successfully!"}, status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            # ❌ Unexpected error occurred
            UserActivityLog.objects.create(
                user=user,
                action="logout",
                status="failed",
                timestamp=now(),
                ip_address=ip_address,
                user_agent=user_agent,
                additional_info={"error": f"An unexpected error occurred: {str(e)}"}, 
            )
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
