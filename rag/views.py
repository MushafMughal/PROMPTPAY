from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication  # ✅ Correct Import
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import json
from .utils import rag_chain
from authentication.utils import CustomAPIException

# Create your views here.
class RAGApi(APIView):
    authentication_classes = [JWTAuthentication]  # ✅ Now this works
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """API to extract structured data from user input (JWT Protected)"""
        try:
            data = request.data  # DRF automatically parses JSON
            user_input = data.get("user_input", "")
            chain = rag_chain()
            result = chain.invoke({"input": user_input})
            
            return Response({"status": True, "data": None, "message": result["answer"]}, status=200)

        except json.JSONDecodeError:
            raise CustomAPIException(False, None, "Invalid JSON format", 400)
        except Exception as e:
            raise CustomAPIException(False, None, str(e), 500)
