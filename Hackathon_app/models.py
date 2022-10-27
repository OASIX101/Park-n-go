from django.db import models
from Hackathon_users.models import CustomUser, Vehicle
from django.forms import model_to_dict

class ParkingSpace(models.Model):
    park_image1  = models.ImageField(upload_to='park/%Y/%B/%d/')
    park_image2 = models.ImageField(upload_to='park/%Y/%B/%d/')
    park_image3 = models.ImageField(upload_to='park/%Y/%B/%d/')
    park_name = models.CharField(max_length=225)
    location_cordinates = models.CharField(max_length=150, unique=True)
    capacity = models.IntegerField()
    available_spaces = models.IntegerField()
    cost_per_hour = models.FloatField() 
    service_fee = models.FloatField()
    discount = models.IntegerField()
    park_info = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.park_name

class Reviews(models.Model):
    user = models.ForeignKey(CustomUser, related_name='user_review', on_delete=models.CASCADE)
    park_space = models.ForeignKey(ParkingSpace, related_name='park_review', on_delete=models.CASCADE)
    review = models.TextField()
    star_ratings = models.FloatField()
    date_added = models.DateField(auto_now_add=True)
    time_added = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.star_ratings

class BookingSpace(models.Model):
    BOOKING_STATUS = (
        ('active', 'active'),
        ('upcoming', 'upcoming'),
        ('past', 'past'),
    )

    parking_space = models.ForeignKey(ParkingSpace, related_name='parking_space', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, related_name='user_booking', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, related_name='vehicle', on_delete=models.CASCADE)
    arrival_date = models.CharField(max_length=100)
    arrival_time = models.CharField(max_length=100)
    departure_date = models.CharField(max_length=100)
    departure_time = models.CharField(max_length=100)
    hours_count = models.IntegerField()
    amount_paid = models.FloatField(default=None, null=True, blank=True)
    booking_status = models.CharField(max_length=25, choices=BOOKING_STATUS, default='upcoming')
    date_booked = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.arrival_date + '_' + self.arrival_time

