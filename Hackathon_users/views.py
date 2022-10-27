from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import logout, authenticate
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from Hackathon_users.models import CustomUser, Vehicle
from .serializers import EmailVerificationSerializer, LogOutSerializer, LogInSerializer, RegisterSerializer, UserEditSerializer, VehicleSerializer, VehicleSerializer2
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .permissions import *
from rest_framework.views import APIView
import math
import random
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from rest_framework import generics, status, views, permissions
from drf_yasg import openapi
import jwt
from .renderers import *
from rest_framework.exceptions import NotFound
from django.conf import settings
import os
from django.http import HttpResponsePermanentRedirect



class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']

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

def email_link(request, user_data):
    user = CustomUser.objects.get(email=user_data['email'])
    token = RefreshToken.for_user(user).access_token
    current_site = get_current_site(request).domain
    relativeLink = reverse('email-verify')
    absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
    email_body = 'Hi '+user.full_name + \
        ' Use the link below to verify your email \n' + absurl
    data = {'email_body': email_body, 'to_email': user.email,
            'email_subject': f'Verify your Park-n-Go email account'}

    Util.send_email(data)
    return Response(user_data, status=status.HTTP_201_CREATED)

class RegisterView(APIView):

    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    @swagger_auto_schema(method='post', request_body=RegisterSerializer())
    @action(methods=['POST'], detail=True)
    def post(self, request):
        user_data = request.data
        if len(user_data['password']) >= 8: 
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
                
                    if obj.is_email_verified == False or obj.is_active == False:
                        obj.delete()

                        serializer1 = self.serializer_class(data=user_data)
                        if serializer1.is_valid():  
                            serializer1.save()
                            email_link(request=request, user_data=user_data)
                            data={
                                'message': 'success',
                                'next_step': 'verify email'
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
        else:
            raise PermissionDenied(detail={'message': 'password is required to be greater than or equal to 8 characteres'})

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
                user.is_active = True
                user.save()
            return Response({'email': 'Successfully activated', 'message': 'move to phone number verfication'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

def email_verif(email):
    try:
        email = CustomUser.objects.get(email=email)
        if email.is_email_verified == True:
            return email
    
    except:
        raise PermissionDenied(detail={'message': 'email has not been verified or does not exist'})

@swagger_auto_schema(method="post",request_body=VehicleSerializer2())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
def add_vehicle(request):
    """this endpoint adds a vehicle to a logged in user"""
    if request.method == 'POST':

        data = request.data
        data['user'] = request.user.id

        serializer = VehicleSerializer(data=data)
        if serializer.is_valid():

            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)

        else:
            data ={
                'message': 'failed',
                'error': serializer.errors
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class VehicleEdit(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOnly]

    def get_vehicle(self, vehicle_id, user):
        try:
            return Vehicle.objects.get(id=vehicle_id, user=user)
        except Vehicle.DoesNotExist:
            raise NotFound(detail={'message': 'vehicle with id does not exist'})

    def get(self, request, vehicle_id, format=None):
        """this retrieves the vehicle with the given id if the vehicle is related to the logged in user"""

        obj = self.get_vehicle(vehicle_id, user=request.user.id)
        serializer = VehicleSerializer(obj)
        data = {
            'message': 'success',
            'data': serializer.data,
         }

        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(method='put', request_body=VehicleSerializer2())
    @action(methods=['PUT'], detail=True)
    def put(self, request, vehicle_id, format=None):
        """this updates the vehicle with the given id if the vehicle is related to the logged in user"""

        obj = self.get_vehicle(vehicle_id, user=request.user.id)
        serializer = VehicleSerializer2(obj, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)

        else:
            data = {
                'message': 'failed',
                'errror': serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method='delete')
    @action(methods=['DELETE'], detail=True)
    def delete(self, request, vehicle_id, format=None):
        """this deletes the vehicle with the given id if the vehicle is related to the logged in user"""
        obj = self.get_vehicle(vehicle_id, user=request.user.id)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
def get_all_vehicle(request):
    """this retrieves all the vehicle related to the logged in user"""

    obj = Vehicle.objects.filter(user=request.user.id)
    serializer = VehicleSerializer(obj, many=True)
    data = {
        'message': 'success',
        'data': serializer.data,
        }

    return Response(data, status=status.HTTP_200_OK)

class UserEdit(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOnly]

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise NotFound(detail={'message': 'Permission denied. User does not exist in the database'})

    def get(self, request,  format=None):
        """this endpoint allows logged in user to retrieve their acct details"""
        obj = self.get_user(user_id=request.user.id)
        serializer = UserEditSerializer(obj)

        data = {
            'message': 'success',
            'data': serializer.data
        }

        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(method='put', request_body=UserEditSerializer())
    @action(methods=['PUT'], detail=True)
    def put(self, request, format=None):
        """this endpoint allows logged in user to update their acct details"""

        obj = self.get_user(user_id=request.user.id)
        serializer = UserEditSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {
                'message': 'success',
            }
            return Response(data, status=status.HTTP_200_OK)

        else:
            data = {
                'message': 'failed',
                'error': serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method='delete')
    @action(methods=['DELETE'], detail=True)
    def delete(self, request, format=None):
        """this endpoint allows logged in user to delete their acct details"""

        obj = self.get_user(user_id=request.user.id)
        obj.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
