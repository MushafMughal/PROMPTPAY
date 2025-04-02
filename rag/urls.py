from django.urls import path
from .views import *


urlpatterns = [
    path("rag/", RAGApi.as_view(), name="rag_query"),

]
