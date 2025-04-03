from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication  # ✅ Correct Import
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .utils import *


class RouterAPI(APIView):
    authentication_classes = [JWTAuthentication]  # ✅ Now this works
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to route user input to the appropriate function (JWT Protected)"""
        try:
            data = request.data  # DRF automatically parses JSON
            user_input = data.get("user_input", "")
            router_response = router(user_input)
            
            if router_response.get("point") == "transfer money":
                respone =  check_missing_info(extract_entities(user_input))
                
                return Response({"status": True, "data": respone.get("data"), "message": respone.get("message"), "route": router_response.get("point")}, status=200)

            else:
                return Response({"status": True, "data": None, "message": router_response.get("message"), "route": None}, status=200)
        

        except json.JSONDecodeError:
            return Response({"status": False, "data": None, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return Response({"status": False, "data": None, "message": str(e)}, status=500)

        
class TransferAPI(APIView):
    authentication_classes = [JWTAuthentication]  # ✅ Now this works
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to extract structured data from user input (JWT Protected)"""
        try:
            data = request.data  # DRF automatically parses JSON
            input_data = data.get("data", "")
            user_input = data.get("user_input", "")
            message = data.get("message", "")

            if data.get("route") == "transfer money":
                respone =  check_missing_info(update_json_data(input_data, user_input, message))
                
                if respone.get("message") == "Completed":
                    respone = confirmation({"data": respone.get("data"), "user_input":None})
                    return Response({"status": True, "data": respone.get("data"), "message": respone.get("confirmation_message"), "route":"complete"}, status=200)
               
                else:
                    return Response({"status": True, "data": respone.get("data"), "message": respone.get("message"), "route":"transfer money"}, status=200)
                
            if data.get("route") == "complete":
                    respone = confirmation({"data": input_data, "user_input":user_input})

                    if respone.get("confirmation_message") == "Proceed":
                        pass
                    else:
                        return Response({"status": True, "data": respone.get("data"), "message": respone.get("confirmation_message"), "route":"complete"}, status=200)

        except json.JSONDecodeError:
            return Response({"status": False, "data": None, "message": "Invalid JSON format", "route": None }, status=400)
        except Exception as e: 
            return Response({"status": False, "data": None, "message": str(e), "route":None}, status=500)



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
        

class CheckMissingInfoAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to check missing fields in the extracted data (JWT Protected)"""
        try:
            data = request.data
            missing_info = check_missing_info(data)
            return Response(missing_info, status=200)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format"}, status=400)

class UpdateDataAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to update extracted JSON data based on user input (JWT Protected)"""
        try:
            data = request.data
            existing_data = data.get("data", {})
            user_response = data.get("user_response", "")
            missing_keys_message = data.get("missing_keys_message", "")

            updated_data = update_json_data(existing_data, user_response, missing_keys_message)
            return Response({"data": updated_data}, status=200)
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

# @csrf_exempt
# def check_missing_info_api(request):
#     """API to check missing fields in the extracted data"""
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             missing_info = check_missing_info(data)
#             return JsonResponse(missing_info, status=200)
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)
    
#     return JsonResponse({"error": "Only POST requests allowed"}, status=405)

# @csrf_exempt
# def update_data_api(request):
#     """API to update extracted JSON data based on user input"""
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             existing_data = data.get("data", {})
#             user_response = data.get("user_response", "")
#             missing_keys_message = data.get("missing_keys_message", "")

#             updated_data = update_json_data(existing_data, user_response, missing_keys_message)
#             return JsonResponse({"data": updated_data}, status=200)
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)
    
#     return JsonResponse({"error": "Only POST requests allowed"}, status=405)


