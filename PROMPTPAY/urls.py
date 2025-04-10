from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),  # Add this line if missing
    path("api/promptpaychatbot/", include("chatbot.urls")),
    path('api/auth/', include('authentication.urls')),  # Authentication URLs
    path('api/core/', include('core_banking.urls')),  # Core banking URLs
    path('api/faqchatbot/', include('rag.urls')),  # RAG URLs
]
