from rest_framework import serializers
from .models import CustomUser

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
        fields = ['first_name','last_name', 'email', 'phone', 'password', 'age', 'phone_otp']

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class RegisterSerializer2(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name', 'email', 'password', 'age']

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class OtpVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=4)
    phone = serializers.CharField(max_length=11)

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = CustomUser
        fields = ['token']

class OtpRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    email = serializers.EmailField()