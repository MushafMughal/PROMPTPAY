from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

class CustomAPIException(APIException):
    def __init__(self, status, data, message, status_code):
        self.status_code = status_code
        self.detail = {  # ✅ This ensures Django treats it as a dictionary response
            "status": status,
            "data": data,
            "message": message
        }
    
    def __str__(self):
        return str(self.detail)  # ✅ Prevents Django from turning it into a string
