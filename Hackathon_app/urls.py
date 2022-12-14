from django.urls import path
from . import views

urlpatterns = [
    path('spaces/', views.ParkingSpaceView1().as_view(), name='spaces'),
    path('spaces/<int:park_id>/', views.ParkingSpaceView2().as_view(), name='space_edit'),
    path('booking/<int:booking_id>/', views.BookingSpaceView().as_view(), name='booking'),
    path('booking/', views.booking, name='space_booking'),
    path('bookings/active/', views.status_active, name='status_active'),
    path('bookings/upcoming/', views.status_upcoming, name='status_upcoming'),
    path('bookings/past/', views.status_past, name='status_past'),
    path('booking/activate/<int:booking_id>/', views.booking_active, name='make_status_active'),
    path('booking/user-all/', views.user_booking, name='user_booking_all'),
    path('booking/checkout/<int:booking_id>/', views.booking_checkout, name='booking_checkout'),
    path('reviews/<int:park_id>/', views.ReviewView().as_view(), name='reviews_all'),
    path('reviews/create/', views.review, name='review_create'),
    path('reviews/update/<int:park_id>/<int:review_id>/', views.ReviewEditView().as_view(), name='review_edit'),
    path('spaces/booking-active/<int:park_id>/',  views.get_all_park_booking_active, name='space_all_booking_active'),
    path('spaces/booking-past/<int:park_id>/',  views.get_all_park_booking_past, name='space_all_booking_past'),
    path('spaces/booking-upcoming/<int:park_id>/',  views.get_all_park_booking_upcoming, name='space_all_booking_upcoming')
]