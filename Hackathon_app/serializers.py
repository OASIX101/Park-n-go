from rest_framework import serializers
from .models import ParkingSpace, Reviews, BookingSpace


class ParkingSpaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParkingSpace
        fields = '__all__'


class BookingSpaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = BookingSpace
        fields = '__all__'

class BookingSpaceSerializer2(serializers.ModelSerializer):

    class Meta:
        model = BookingSpace
        fields = ['parking_space', 'vehicle', 'arrival_date', 'arrival_time', 'departure_date', 'departure_time', 'hours_count', 'amount_paid']


class ReviewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = '__all__'


class ReviewsSerializer2(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = ['park_space', 'review', 'star_ratings']

class ReviewsSerializer3(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = ['review', 'star_ratings']
