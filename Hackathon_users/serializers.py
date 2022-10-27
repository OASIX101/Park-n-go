from rest_framework import serializers
from .models import CustomUser, Vehicle
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class LogInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100, min_length=8)

class LogOutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=500)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'password', 'age', 'gmail_uid', 'user_image']

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = CustomUser
        fields = ['token']

class VehicleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = '__all__'

class VehicleSerializer2(serializers.ModelSerializer):

    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'license_plate_number', 'car_model']

class UserEditSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = CustomUser
        fields = ['full_name', 'age']
