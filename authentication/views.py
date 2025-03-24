from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated 
from rest_framework_simplejwt.tokens import RefreshToken
from .models import BlacklistedAccessToken
from django.core.cache import cache


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


# ✅ Login user and get token
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username  # Custom claim
        token["user_id"] = user.id
        return token

    def validate(self, attrs):
        username_or_email_or_cnic = attrs.get("username")  # DRF default expects 'username'
        password = attrs.get("password")

        user = None
        if "@" in username_or_email_or_cnic:  # Login via email
            user = User.objects.filter(email=username_or_email_or_cnic).first()
        elif username_or_email_or_cnic.isdigit():  # Login via CNIC
            user = User.objects.filter(cnic=username_or_email_or_cnic).first()
        else:  # Login via username
            user = User.objects.filter(username=username_or_email_or_cnic).first()

        if not user or not check_password(password, user.password):  # Use check_password for hashing
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:  # Prevent inactive users from logging in
            raise AuthenticationFailed("User account is inactive.")

        data = super().validate({"username": user.username, "password": password})  # Generate tokens
        data["username"] = user.username  # Add username to response
        data["user_cnic"] = user.cnic  # Add CNIC to response
        data["user_id"] = user.id  # Add user ID to response
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# ✅ Logout user and blacklist refresh token
class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            access_token = request.auth  # Get access token from request header
            # ✅ Blacklist Refresh Token
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    return Response({"error": "Invalid or already blacklisted refresh token"}, status=status.HTTP_400_BAD_REQUEST)
            
            # ✅ Blacklist Access Token (custom method)
            if access_token:
                token_str = str(access_token)
                # Avoid duplicate entries
                if not BlacklistedAccessToken.objects.filter(token=token_str).exists():
                    BlacklistedAccessToken.objects.create(token=token_str)
                # ✅ Remove from cache immediately
                cache.set(f"blacklisted_{token_str}", True, timeout=3600)
            return Response({"message": "Logged out successfully!"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid token or already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)
