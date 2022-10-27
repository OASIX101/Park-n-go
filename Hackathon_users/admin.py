from django.contrib import admin
from .models import Vehicle, CustomUser

@admin.register(Vehicle)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_plate_number', 'car_model', 'vehicle_type')
    list_filter = ('car_model', 'user', 'license_plate_number', 'vehicle_type')
    search_fields = ('car_model', 'user', 'license_plate_number', 'vehicle_type')
    raw_id_fields = ('user',)
    list_editable = ['car_model','license_plate_number', 'vehicle_type']

@admin.register(CustomUser)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'email', 'is_staff', 'is_superuser', 'is_email_verified')
    list_filter = ('full_name', 'age', 'email', 'is_staff', 'is_superuser', 'is_email_verified')
    search_fields = ('full_name', 'age', 'email', 'is_staff', 'is_superuser', 'is_email_verified')
    list_editable = ['age', 'email', 'is_staff', 'is_superuser']