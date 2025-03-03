from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),  # Add this line if missing
    path("api/", include("chatbot.urls")),
]
