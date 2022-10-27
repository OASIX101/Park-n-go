from django.urls import path, include
from . import views

urlpatterns = [
    path('access/', include('djoser.urls.jwt')),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('register/', views.RegisterView().as_view()),
    path('email-verify/', views.VerifyEmail.as_view(), name="email-verify"),
    path('phone-verify/', views.verify_otp, name="phone_otp_verify"),
    path('request-otp/', views.request_otp, name="request_otp"),
    path('vehicle/', views.add_vehicle, name="vehicle"),
    path('vehicle/<int:vehicle_id>/', views.VehicleEdit().as_view(), name="vehicle"),
    path('vehicles/', views.get_all_vehicle, name="all_vehicles")
]