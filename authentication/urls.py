from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='user-register'),
    path('updateaccountdetails/', update_user_details, name='update_user_account'),
    path('updatepassword/', update_password, name='update_password'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("logout/", LogoutAPI.as_view(), name="logout"),
    path("verify-otp/", VerifyOTPAPI.as_view(), name="verify_otp"),
    path("resend-otp/", ResendOTPAPI.as_view(), name="resend_otp"),
]

