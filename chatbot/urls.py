from django.urls import path
from .views import *


urlpatterns = [
    path("router/", RouterAPI.as_view(), name="chat"),
    path("transfer-money/", TransferAPI.as_view(), name="Transfer Money"),
    path("bill-payment/", PayBillAPI.as_view(), name="Pay Bill"),
    path("change-password/", ChangePasswordAPI.as_view(), name="Change Password"),
]
