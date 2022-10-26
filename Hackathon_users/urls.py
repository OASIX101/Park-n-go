from django.urls import path, include
from . import views

urlpatterns = [
    path('access/', include('djoser.urls.jwt')),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('register/', views.RegisterView().as_view())
]