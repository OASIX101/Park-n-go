from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import logout, authenticate
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from Hackathon_users.models import CustomUser
from .serializers import LogOutSerializer, LogInSerializer, OtpVerifySerializer, RegisterSerializer, RegisterSerializer2
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .permissions import *
from rest_framework.views import APIView
import math
import random
from .mixins import *

@swagger_auto_schema(method="post",request_body=LogInSerializer())
@api_view(["POST"])
def login_view(request):
    
    if request.method == "POST":
        
        serializer = LogInSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(request, username = serializer.validated_data['email'], password = serializer.validated_data['password'])
        if user:
            if user.is_active:
                try:
                    refresh = RefreshToken.for_user(user)
                    
                    user_details = {}
                    user_details['id']   = user.id
                    user_details['username'] = user.first_name + ' ' + user.last_name
                    user_details['email'] = user.email
                    user_details['refresh_token'] = str(refresh)
                    user_details['access_token'] = str(refresh.access_token)
                    user_logged_in.send(sender=user.__class__,
                                        request=request, user=user)

                    data = {
                    'message' : "success",
                    'data' : user_details,
                    }
        
                    return Response(data, status=status.HTTP_200_OK)


                except Exception as e:
                    raise e
            
            else:
                data = {
                    'message'  : "failed",
                    'errors': 'This account is not active'
                    }
                return Response(data, status=status.HTTP_403_FORBIDDEN)


        else:
            data = {
                'message'  : "failed",
                'errors': 'Please provide a valid username and password'
                }
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method="post",request_body=LogOutSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
def logout_view(request):
    """Log out a user by blacklisting their refresh token then making use of django's internal logout function to flush out their session and completely log them out.
    Returns:
        Json response with message of success and status code of 204.
    """
    
    serializer = LogOutSerializer(data=request.data)
    
    serializer.is_valid()
    
    try:
        token = RefreshToken(token=serializer.validated_data["refresh_token"])
        token.blacklist()
        user=request.user
        user_logged_out.send(sender=user.__class__,
                                        request=request, user=user)
        logout(request)
        
        return Response({"message": "success"}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({"message": "failed", "error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

class RegisterView(APIView):

    serializer_class = RegisterSerializer

    @swagger_auto_schema(method='post', request_body=RegisterSerializer2())
    @action(methods=['POST'], detail=True)
    def post(self, request):
        user_data = request.data
        user_data['phone_otp'] = generateOTP()

        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone'] 
            sms = MessageHandler(f'+234{phone}', serializer.validated_data['phone_otp'])
            sms.send_otp_to_phone()
            serializer.save()
            data={
                'message': 'success',
                'next_step': 'move to otp verification endpoint'
            }

            return Response(data, status=status.HTTP_201_CREATED)


        else:
            obj = CustomUser.objects.get(email=user_data['email'], phone=user_data['phone'])
        
            if obj.is_otp_verified == False or obj.is_email_verified == False:
                obj.delete()

                serializer1 = self.serializer_class(data=user_data)
                if serializer1.is_valid():
                    phone = serializer1.validated_data['phone'] 
                    sms = MessageHandler(f'+234{phone}', serializer1.validated_data['phone_otp'])
                    sms.send_otp_to_phone()
                    serializer1.save()
                    data={
                        'message': 'success',
                        'next_step': 'move to otp verification endpoint'
                    }

                    return Response(data, status=status.HTTP_201_CREATED)

                else:
                    data = {
                        'error': 'an error occured try again'
                    }

                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

            else:
                data = {
                    'message': 'failed to create. user already exists',
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method="post",request_body=OtpVerifySerializer())
@api_view(["POST"])
def OtpVerify(request):
    if request.method == "POST":
        obj = CustomUser.objects.get(phone=request.data['phone'])
        if obj:
            otp = request.data['phone_otp']
        





        