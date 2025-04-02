from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User  # Import User model
import re
from datetime import datetime
from .utils import CustomAPIException


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name','cnic', 'username', 'email','dob', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Hide password in response

    # def create(self, validated_data):
    #     validated_data['password'] = make_password(validated_data['password'])  # Hash password
    #     return super().create(validated_data)


    def create(self, validated_data):
        password = validated_data.get('password')

        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search("[A-Za-z]", password) or not re.search("[0-9]", password):
            raise serializers.ValidationError("Password must contain both letters and numbers.")

        validated_data['password'] = make_password(password)  # Hash password
        return super().create(validated_data)

    # Custom field validations
    def validate_name(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Name cannot be empty.")
        return value
    
    def validate_username(self, value):
        if not re.match("^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError("Username must be alphanumeric.")
        if len(value) < 6 or len(value) > 15:
            raise serializers.ValidationError("Username must be between 6 and 15 characters.")
        return value
    
    def validate_cnic(self, value):
        if len(value) != 13 or not value.isdigit():
            raise serializers.ValidationError("CNIC must be 13 digits.")
        return value
    
    def validate_email(self, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise serializers.ValidationError("Invalid email format.")
        return value
    
    def validate_phone_number(self, value):

        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits.")

        if not re.match(r"^\+92\d{10}$", value):
            raise serializers.ValidationError("Phone number must be in the format +92xxxxxxxxx.")
        return value
    
    def validate_dob(self, value):
        if (datetime.now().year - value.year) < 18:
            raise serializers.ValidationError("User must be at least 18 years old.")
        return value
    