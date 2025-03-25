from django.urls import path
from .views import *

urlpatterns = [
    path('accountdetails/', get_user_details, name='get_user_account'),
    path('carddetails/', get_card_details, name='card-details'),
    path('payeedetails/', manage_payees, name='manage-payees'),
    path('transactionslist/', list_transactions, name='list-transactions'),
    path('transactiondetails/<str:transaction_id>/', transaction_details, name='transaction-details'),
]