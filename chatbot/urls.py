from django.urls import path
from .views import *


urlpatterns = [
    path("router/", RouterAPI.as_view(), name="chat"),
    path("transfer-money/", TransferAPI.as_view(), name="Transfer Money"),
    path("check-missing/", CheckMissingInfoAPI.as_view(), name="check_missing"),
    path("update/", UpdateDataAPI.as_view(), name="update_data"),
]
