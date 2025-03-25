from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

class CustomAPIException(APIException):
    def __init__(self, message, status_code):
        self.status_code = status_code
        self.detail = {"error": message}