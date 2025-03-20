from django.urls import path
from .views import *


urlpatterns = [
    path("promptpay/extract/", ExtractDataAPI.as_view(), name="extract_data"),
    path("promptpay/check-missing/", check_missing_info_api, name="check_missing"),
    path("promptpay/update/", update_data_api, name="update_data"),
    
]
