from django.urls import path
from .views import *
urlpatterns = [
    path("extract/", extract_data_api, name="extract_data"),
    path("check-missing/", check_missing_info_api, name="check_missing"),
    path("update/", update_data_api, name="update_data"),
    path("add-user/", add_user, name="add_user"),
    path("get-users/", get_users, name="get_users")
    
]
