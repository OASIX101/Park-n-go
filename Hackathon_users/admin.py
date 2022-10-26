from django.contrib import admin
from .models import Vehicle, CustomUser

admin.site.register([Vehicle, CustomUser])