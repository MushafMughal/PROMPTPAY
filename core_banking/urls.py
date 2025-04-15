from django.urls import path
from .views import *

urlpatterns = [
    path('accountdetails/', get_user_details, name='get_user_account'),
    path('carddetails/', get_card_details, name='card-details'),
    path('updatecarddetails/', update_card_limit, name='update-card-limit'),
    path('getpayees/', get_payees, name='get-payees'),
    path('addpayee/', add_payee, name='add-payee'),
    path('transactionlist/', list_transactions, name='list-transactions'),
    path('transactionlist/<str:transaction_id>/', transaction_details, name='transaction-details'),
    path('sendmoney/', send_money, name='send-money'),
]