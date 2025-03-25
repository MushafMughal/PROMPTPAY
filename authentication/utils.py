from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status

# def custom_jwt_exception_handler(exc, context):
#     response = exception_handler(exc, context)

#     if isinstance(exc, InvalidToken):
#         # Check if it's an expired token
#         if "Token is invalid or expired" in str(exc):
#             return Response(
#                 {"error": "Token has expired"}, 
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
#         return Response(
#             {"error": "Invalid token"}, 
#             status=status.HTTP_401_UNAUTHORIZED
#         )

#     return response
