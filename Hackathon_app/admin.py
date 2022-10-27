from django.contrib import admin
from .models import BookingSpace, ParkingSpace, Reviews

@admin.register(BookingSpace)
class BookgingAdmin(admin.ModelAdmin):
    list_display = ('parking_space', 'user', 'vehicle', 'arrival_date', 'arrival_time')
    list_filter = ('parking_space', 'user', 'vehicle', 'arrival_date', 'arrival_time')
    search_fields = ('parking_space', 'user', 'vehicle', 'arrival_date', 'arrival_time')
    raw_id_fields = ('parking_space', 'user', 'vehicle')
    list_editable = ['user', 'vehicle', 'arrival_date', 'arrival_time']
    
@admin.register(ParkingSpace)
class ParkAdmin(admin.ModelAdmin):
    list_display = ('park_name', 'location_coordinates', 'cost_per_hour', 'capacity', 'available_spaces')
    list_filter = ('park_name', 'location_coordinates', 'cost_per_hour', 'capacity', 'available_spaces')
    search_fields = ('park_name', 'location_coordinates', 'cost_per_hour', 'capacity', 'available_spaces')
    list_editable = ['location_coordinates', 'cost_per_hour', 'capacity', 'available_spaces']

@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'review', 'star_ratings', 'park_space')
    list_filter = ('star_ratings', 'user')
    search_fields = ('star_ratings', 'user', 'park_space')
    raw_id_fields = ('user', 'park_space')
    list_editable = ['review', 'star_ratings']