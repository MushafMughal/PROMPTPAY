from django.urls import path
from .views import *


urlpatterns = [
    path("extract/", ExtractDataAPI.as_view(), name="extract_data"),
    path("check-missing/", CheckMissingInfoAPI.as_view(), name="check_missing"),
    path("update/", UpdateDataAPI.as_view(), name="update_data"),
    
]
