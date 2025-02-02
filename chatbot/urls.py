from django.urls import path
from .views import extract_data_api, check_missing_info_api, update_data_api

urlpatterns = [
    path("extract/", extract_data_api, name="extract_data"),
    path("check-missing/", check_missing_info_api, name="check_missing"),
    path("update/", update_data_api, name="update_data"),
]
