from django.urls import path
from .views import *

urlpatterns = [
    path('accountdetails/', get_user_details, name='get_user_account'),
    path('carddetails/', get_card_details, name='card-details'),


]
