from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import logout, authenticate
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from Hackathon_users.models import CustomUser
from .serializers import EmailVerificationSerializer, LogOutSerializer, LogInSerializer, OtpRequestSerializer, OtpVerifySerializer, RegisterSerializer, RegisterSerializer2
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .permissions import *
from rest_framework.views import APIView
import math
import random
from .mixins import *
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from rest_framework import generics, status, views, permissions
from drf_yasg import openapi
import jwt
from .renderers import *
from rest_framework.exceptions import NotFound

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

def email_link(request, user_data):
    user = CustomUser.objects.get(email=user_data['email'])
    token = RefreshToken.for_user(user).access_token
    current_site = get_current_site(request).domain
    relativeLink = reverse('email-verify')
    absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
    email_body = 'Hi '+user.first_name + '' + user.last_name + \
        ' Use the link below to verify your email \n' + absurl
    data = {'email_body': email_body, 'to_email': user.email,
            'email_subject': f'Verify your Park-n-Go email account'}

    Util.send_email(data)
    return Response(user_data, status=status.HTTP_201_CREATED)

def otp(phone, otp):
    if phone[0] == '0':
        phone_num = phone[1:]
        sms = MessageHandler(f'+234{phone_num}', otp)
        sms.send_otp_to_phone() 
    
    else:
        sms = MessageHandler(f'+234{phone}', otp)
        sms.send_otp_to_phone() 

class RegisterView(APIView):

    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    @swagger_auto_schema(method='post', request_body=RegisterSerializer2())
    @action(methods=['POST'], detail=True)
    def post(self, request):
        user_data = request.data

        if eval(user_data['age']) >= 18:
            serializer = self.serializer_class(data=user_data)
            if serializer.is_valid():
                serializer.save()
                email_link(request=request, user_data=user_data)
                data={
                    'message': 'success',
                    'verify': 'verify email'
                }

                return Response(data, status=status.HTTP_201_CREATED)

            
        
            else:
                obj = CustomUser.objects.get(email=user_data['email'])
            
                if obj.is_otp_verified == False or obj.is_email_verified == False:
                    obj.delete()

                    serializer1 = self.serializer_class(data=user_data)
                    if serializer1.is_valid():  
                        serializer1.save()
                        email_link(request=request, user_data=user_data)
                        data={
                            'message': 'success',
                            'next_page': 'verify email'
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
        else:
            data = {
                'message': 'failed to create. People below 18 cannot be allowed to register',
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = CustomUser.objects.get(id=payload['user_id'])
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
            return Response({'email': 'Successfully activated', 'message': 'move to phone number verfication'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method="post",request_body=OtpVerifySerializer())
@api_view(["POST"])
def verify_otp(request):
    if request.method == "POST":
        phone=request.data['phone']
        try:    
            obj = CustomUser.objects.get(phone=request.data['phone'])
            if obj:
                if obj.is_email_verified == True:
                    otp = request.data['otp']
                    if obj.phone_otp == otp:
                        obj.is_active = True
                        obj.is_otp_verified = True
                        obj.phone_otp = ''
                        obj.save()

                        data = {
                            'message': 'phone number verified. Account is now active.'
                        }
                        return Response(data, status=status.HTTP_200_OK)

                    else:
                        data = {
                            'otp is not valid'
                        }
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(data={'message': 'email has not been verified'}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            raise NotFound(detail={'message': 'Permission denied. Phone number not found in the database'})


def email_verif(email):
    try:
        email = CustomUser.objects.get(email=email)
        if email.is_email_verified == True:
            return email
    
    except:
        raise PermissionDenied(detail={'message': 'email has not been verified or does not exist'})

@swagger_auto_schema(method="post",request_body=OtpRequestSerializer())
@api_view(["POST"])
def request_otp(request):
    data = request.data
    phone = data['phone']   
    email=data['email']
 
    email2 = email_verif(email)
    try:
        phone_check = CustomUser.objects.filter(phone=phone)
        if phone_check != []:
            email2.phone = phone
            email2.phone_otp = generateOTP()
            email2.save()
            otp(email2.phone, email2.phone_otp)
            return Response(data={'message': 'phone otp sent'})            
        else:
            raise PermissionDenied(detail={'message': 'this number is already ien use by another account'})
            
    except CustomUser.DoesNotExist:
            raise PermissionDenied(detail={'message': 'this number ris already in use by another account'})


