from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication  # ✅ Correct Import
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .utils import *


class ExtractDataAPI(APIView):
    authentication_classes = [JWTAuthentication]  # ✅ Now this works
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to extract structured data from user input (JWT Protected)"""
        try:
            data = request.data  # DRF automatically parses JSON
            user_input = data.get("user_input", "")
            extracted_data = extract_entities(user_input)
            return Response({"data": extracted_data}, status=200)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format"}, status=400)

# @csrf_exempt
# def extract_data_api(request):
#     """API to extract structured data from user input"""
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             user_input = data.get("user_input", "")
#             extracted_data = extract_entities(user_input)
#             return JsonResponse({"data": extracted_data}, status=200)
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)
    
#     return JsonResponse({"error": "Only POST requests allowed"}, status=405)

@csrf_exempt
def check_missing_info_api(request):
    """API to check missing fields in the extracted data"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            missing_info = check_missing_info(data)
            return JsonResponse(missing_info, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    
    return JsonResponse({"error": "Only POST requests allowed"}, status=405)

@csrf_exempt
def update_data_api(request):
    """API to update extracted JSON data based on user input"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            existing_data = data.get("data", {})
            user_response = data.get("user_response", "")
            missing_keys_message = data.get("missing_keys_message", "")

            updated_data = update_json_data(existing_data, user_response, missing_keys_message)
            return JsonResponse({"data": updated_data}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    
    return JsonResponse({"error": "Only POST requests allowed"}, status=405)


