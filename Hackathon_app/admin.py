from django.contrib import admin
from .models import BookingSpace, ParkingSpace, Reviews

admin.site.register([BookingSpace, ParkingSpace, Reviews])
