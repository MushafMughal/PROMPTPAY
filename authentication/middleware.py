from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache  # Import cache
from .models import BlacklistedAccessToken

class BlockBlacklistedTokensMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]  # Extract token

            # ✅ Check cache first to avoid unnecessary DB queries
            if cache.get(f"blacklisted_{access_token}"):
                return JsonResponse({"error": "Access token is invalid. Please log in again."}, status=401)

            # ✅ Query database only if not found in cache
            if BlacklistedAccessToken.objects.filter(token=access_token).exists():
                cache.set(f"blacklisted_{access_token}", True, timeout=3600)  # Cache for 1 hour
                return JsonResponse({"error": "Access token is invalid. Please log in again."}, status=401)
