from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .models import BlacklistedAccessToken

class BlockBlacklistedTokensMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]  # Extract token
            if BlacklistedAccessToken.objects.filter(token=access_token).exists():
                return JsonResponse({"error": "Access token is invalid. Please log in again."}, status=401)
