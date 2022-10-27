from .serializers import BookingSpaceSerializer, BookingSpaceSerializer2, ParkingSpaceSerializer, ReviewsSerializer, ReviewsSerializer2, ReviewsSerializer3
from rest_framework.decorators import action, authentication_classes, permission_classes, api_view
from rest_framework.exceptions import NotFound, PermissionDenied, NotAcceptable
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from Hackathon_users.models import Vehicle
from .models import BookingSpace, Reviews, ParkingSpace
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import status
from Hackathon_users.permissions import *

# <--parking endpoints -->
class ParkingSpaceView1(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, format=None):
        """this endpoint is retrieves the parking spaces available in the database. allows only admin to create but allows other users to read only"""

        obj = ParkingSpace.objects.all()
        serializer = ParkingSpaceSerializer(obj, many=True)

        data = {
            'message': 'success',
            'data': serializer.data
        }

        return Response(data=data , status=status.HTTP_200_OK)

    @swagger_auto_schema(method='post', request_body=ParkingSpaceSerializer())
    @action(methods=['POST'], detail=True)
    def post(self, request, format=None):
        """this endpoint creates a new parking space to the database. it allows all users and allows anonymous users to read only"""

        serializer = ParkingSpaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            data = {
                'message': 'success',
            }
            return Response(data, status=status.HTTP_200_OK)

        else:
            
            data = {
                'message': 'failed',
                'error(s)': serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class ParkingSpaceView2(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get_parking_space(self, park_id):
        """trys to get the park with the given id. Returns an error message if park not found"""
        try:
            return ParkingSpace.objects.get(id=park_id)
        except ParkingSpace.DoesNotExist:
            raise NotFound(detail={'message': 'parking space with id not found'}) 

    def get(self, request, park_id, format=None):
        """this endpoint retrieves all bookings that are active for a park"""

        obj = self.get_parking_space(park_id)
        serializer = ParkingSpaceSerializer(obj)
        data = {
            'message': 'success',
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK) 

    @swagger_auto_schema(method='put', request_body=ParkingSpaceSerializer())
    @action(methods=['PUT'], detail=True)
    def put(self, request, park_id, format=None):
        """this endpoint update the entire or partial details of the park with the girven id"""

        obj = self.get_parking_space(park_id)
        serializer = ParkingSpaceSerializer(obj, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            data = {
                'message': 'success',
            }
            return Response(data, status=status.HTTP_200_OK)

        else:
            
            data = {
                'message': 'failed',
                'error(s)': serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method='delete')
    @action(methods=['DELETE'], detail=True)      
    def delete(self, request, park_id, format=None):
        """this endpoint deletes the park with given id"""
        obj = self.get_parking_space(park_id)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# <-- booking endpoints -->
class BookingSpaceView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOnly]

    def get_booking(self, user, booking_id):
        """trys to get the booking of the currently logged in user with the given id. Returns an error message if booking not found"""
        try:
            return BookingSpace.objects.get(id=booking_id, user=user)
        except BookingSpace.DoesNotExist:
            raise NotFound(detail={'message': 'booking with id and user not found'}) 

    def get(self, request, booking_id, format=None):
        """this endpoint gets a single booking of the currently logged in user"""
        
        obj = self.get_booking(user=request.user.id, booking_id=booking_id)
        serializer = BookingSpaceSerializer(obj)

        data = {
            'message': 'success',
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(method='delete')
    @action(methods=['DELETE'], detail=True)
    def delete(self, request, booking_id, format=None):
        """this endpoint deletes a single booking of the currently logged in user if the booking is upcoming""" 

        obj = self.get_booking(user=request.user.id, booking_id=booking_id)
        if obj.booking_status == 'upcoming':
            park = obj.parking_space.id
            park_obj = ParkingSpace.objects.get(id=park)
            park_obj.available_spaces+=1
            park_obj.save()
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            raise PermissionDenied(detail={'message': 'Booking cannot be canceled because booking is active or has already been checked out.'})

@swagger_auto_schema(method='post', request_body=BookingSpaceSerializer2())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
def booking(request):
    """this endpoint creates a new booking for the logged in user if the amount_paid was provided and the vehicle provided is registered under the user"""
    if request.method == 'POST':
        data = request.data
        data['user'] = request.user.id
        data['booking_status'] = 'upcoming'

        vehicle = int(data['vehicle'])
        try:
            vehicle_obj = Vehicle.objects.get(id=vehicle)
            if vehicle_obj.user.id == int(data['user']):

                if data['amount_paid'] != 0 and data['amount_paid'] != '':

                    serializer = BookingSpaceSerializer(data=request.data)
                    if serializer.is_valid():

                        park = serializer.validated_data['parking_space'].id
                        park_obj = ParkingSpace.objects.get(id=park)
                        if park_obj.available_spaces > 0:
                            park_obj.available_spaces-=1
                            park_obj.save()
                            serializer.save()
                            return Response(data, status=status.HTTP_200_OK)
                        
                        else:
                            raise PermissionDenied(detail={'message': 'there is currently no space available for this park. Try again later.'})

                    else:
                        data = {
                            'message': 'failed',
                            'data': serializer.errors
                        }
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)

                else:
                    raise NotAcceptable(detail={'message': 'an error occured in the payment'})

            else:
                raise PermissionDenied(detail={'message': 'Vehicle is not registered under this user'})
        except Vehicle.DoesNotExist:
            raise NotFound(detail={'message': 'Vehicle with id does not exist'})

@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
@api_view(['GET'])
def status_active(request):
    """this endpoint retrieves all booking for the logged in user from the database that are currently active"""
    if request.method == 'GET':
        obj = BookingSpace.objects.filter(booking_status='active', user=request.user.id)
        serializer = BookingSpaceSerializer(obj, many=True)
        data = {
            'message': 'success',
            'count': obj.count(),
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
@api_view(['GET'])
def status_upcoming(request):
    """this endpoint retrieves all booking for the logged in user from the database that are upcoming"""

    if request.method == 'GET':
        obj = BookingSpace.objects.filter(booking_status='upcoming', user=request.user.id)
        serializer = BookingSpaceSerializer(obj, many=True)
        data = {
            'message': 'success',
            'count': obj.count(),
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
@api_view(['GET'])
def status_past(request):
    """this endpoint retrieves all booking for the logged in user from the database that have been checked out"""

    if request.method == 'GET':
        obj = BookingSpace.objects.filter(booking_status='past', user=request.user.id)
        serializer = BookingSpaceSerializer(obj, many=True)
        data = {
            'message': 'success',
            'count': obj.count(),
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
@api_view(['GET'])
def user_booking(request):
    """this endpoint retrieves all booking for the logged in user from the database regardless of their status."""

    if request.method == 'GET':
        obj = BookingSpace.objects.filter(user=request.user.id)
        serializer = BookingSpaceSerializer(obj, many=True)
        data = {
            'message': 'success',
            'count': obj.count(),
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
@api_view(['GET'])
def booking_checkout(request, booking_id):
    """trys to get the booking of the currently logged in user with the given id and checks the booking out if the booking is active. Returns an error message if booking not found"""
    try:
        obj = BookingSpace.objects.get(id=booking_id, user=request.user.id)
        if obj.booking_status == 'active':
            park = obj.parking_space.id
            park_obj = ParkingSpace.objects.get(id=park)
            park_obj.available_spaces+=1
            park_obj.save()
            obj.booking_status = 'past'
            obj.save()
        else:
            raise PermissionDenied(detail={'message': 'Booking cannot be checked because booking is upcoming or has already been checked out.'})
     
    except BookingSpace.DoesNotExist:
        raise NotFound(detail={'message': 'booking with id not found'}) 

@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
@api_view(['GET'])
def booking_active(request, booking_id):
    """trys to get the booking of the currently logged in user with the given id and make the booking active if the booking status is upcoming. Returns an error message if booking not found"""
    try:
        obj = BookingSpace.objects.get(id=booking_id, user=request.user.id)
        if obj.booking_status == 'upcoming':
            obj.booking_status = 'active'
            obj.save()
        else:
            raise PermissionDenied(detail={'message': 'Booking cannot be made active because booking is active or has already been checked out.'})
     
    except BookingSpace.DoesNotExist:
        raise NotFound(detail={'message': 'booking with id not found'}) 

@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminOnly])
@api_view(['GET'])
def get_all_park_booking_active(request, park_id):
    """this endpoint retrieves all bookings that are active for a single park"""
    try:
        obj = ParkingSpace.objects.get(id=park_id)
        objs = obj.parking_space.filter(booking_status='active')
        serializer = BookingSpaceSerializer(objs, many=True)
        data = {
            'message': 'success',
            'count': objs.count(),
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK) 

    except ParkingSpace.DoesNotExist:
        raise NotFound(detail={'message': 'parking space with id not found'}) 

@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminOnly])
@api_view(['GET'])
def get_all_park_booking_upcoming(request, park_id):
    """this endpoint retrieves all bookings that are upcoming for a single park"""
    try:
        obj = ParkingSpace.objects.get(id=park_id)
        objs = obj.parking_space.filter(booking_status='upcoming')
        serializer = BookingSpaceSerializer(objs, many=True)
        data = {
            'message': 'success',
            'count': objs.count(),
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK) 

    except ParkingSpace.DoesNotExist:
        raise NotFound(detail={'message': 'parking space with id not found'}) 

# <-- Reviews endpoints -->
class ReviewView(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOnly]

    def get_parking_space(self, park_id):
        """trys to get the park with the given id. Returns an error message if park not found"""
        try:
            return ParkingSpace.objects.get(id=park_id)
        except ParkingSpace.DoesNotExist:
            raise NotFound(detail={'message': 'parking space with id not found'}) 

    def get(self, request, park_id, format=None):
        """this endpoint retrieves all the review related to a parking space"""

        obj = self.get_parking_space(park_id)
        objs = obj.park_review.all()
        serializer = ReviewsSerializer(objs, many=True)
        data = {
            'message': 'data',
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

@swagger_auto_schema(method='post', request_body=ReviewsSerializer2())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsUserOnly])
def review(request):
    """this endpoint create new reviews to the database"""
    if request.method == 'POST':
        data = request.data
        data['user'] = request.user.id

        obj = ReviewsSerializer(data=data)
        if obj.is_valid():
            obj.save()

            data = {
                'message': 'success',           
            }
            return Response(data, status=status.HTTP_200_OK)

        else:
            data = {
                'message': 'failed',
                'error': obj.data
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

class ReviewEditView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOnly]

    def get_review(self, park_id, review_id, user):
        """this endpoint retrieves the review for the given park relating to the logged in user"""
        try:
            park = ParkingSpace.objects.get(id=park_id)
            park_obj = park.park_review.get(id=review_id, user=user)
            if park_obj:
                return park_obj
            else:
                raise PermissionDenied(detail={'message': 'cannot update review. review is not for this user'})

        except ParkingSpace.DoesNotExist:
            raise NotFound(detail={'message': 'parking space with id not found'}) 
     
    def get(self, request, park_id, review_id, format=None):
        """this endpoint retrieves review with the given id if the park_id and user are related to the given review"""
        user = request.user.id
        obj = self.get_review(park_id, review_id, user)
        serilaizer = ReviewsSerializer(obj)
        data = {
            'message': 'success',
            'data': serilaizer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(method='post', request_body=ReviewsSerializer3())
    @action(methods=['POST'], detail=True)
    def put(self, request, park_id, review_id, user):
        """this endpoint updates review with the given id if the park_id and user are related to the given review"""
        user = request.user.id
        obj = self.get_review(park_id, review_id, user)
        serializer = ReviewsSerializer3(obj, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            data = {
                'message': 'success',
            }
            return Response(data, status=status.HTTP_200_OK)

        else:
            data = {
                'message': 'failed',
                'error(s)': serializer.errors
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(method='post')
    @action(methods=['POST'], detail=True)
    def delete(self, request, park_id, review_id, user):
        user = request.user.id
        obj = self.get_review(park_id, review_id, user)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

############     Oasix.com       ################