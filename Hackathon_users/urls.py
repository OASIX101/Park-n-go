from django.urls import path, include
from . import views

urlpatterns = [
    path('access/', include('djoser.urls.jwt')),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('register/', views.RegisterView().as_view()),
    path('email-verify/', views.VerifyEmail.as_view(), name="email_verify"),
    path('vehicle/', views.add_vehicle, name="vehicle"),
    path('vehicle/<int:vehicle_id>/', views.VehicleEdit().as_view(), name="vehicle"),
    path('vehicles/', views.get_all_vehicle, name="all_vehicles"),
    path('user-details/', views.UserEdit().as_view(), name="user_details"),
]