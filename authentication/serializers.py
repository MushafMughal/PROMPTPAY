from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User  # Import User model

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name','cnic', 'username', 'email','dob', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Hide password in response

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hash password
        return super().create(validated_data)
