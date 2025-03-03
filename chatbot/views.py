from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import extract_entities, check_missing_info, update_json_data
from .models import UserDetails


@csrf_exempt
def extract_data_api(request):
    """API to extract structured data from user input"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("user_input", "")
            extracted_data = extract_entities(user_input)
            return JsonResponse({"data": extracted_data}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
    
    return JsonResponse({"error": "Only POST requests allowed"}, status=405)

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

@csrf_exempt
def add_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if not all(key in data for key in ["first_name", "last_name", "email", "phone_number"]):
            return JsonResponse({"error": "Missing required fields"}, status=400)
        if UserDetails.objects.filter(email=data.get("email")).exists():
            return JsonResponse({"error": "User with this email already exists"}, status=400)
        if UserDetails.objects.filter(phone_number=data.get("phone_number")).exists():
            return JsonResponse({"error": "User with this phone number already exists"}, status=400)
        user = UserDetails.objects.create(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            phone_number=data.get("phone_number"),
            address=data.get("address", "")
        )
        return JsonResponse({"message": "User added successfully!", "user_id": user.first_name}, status=201)
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def get_users(request):
    if request.method == "GET":
        users = UserDetails.objects.values()  # Get all user data
        return JsonResponse(list(users), safe=False)
    else:
        return JsonResponse({"error": "Only GET requests allowed"}, status=405)

