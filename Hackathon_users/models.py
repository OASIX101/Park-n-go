from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, full_name, user_image, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            full_name=full_name,
            **other_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, full_name, user_image, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)


        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.'
            )

        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.'
            )

        return self.create_user(email, password, full_name, **other_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):

    user_image = models.ImageField(upload_to='user_image/%Y/%B/%d/', null=True, blank=True)
    email = models.EmailField(unique=True)
    gmail_uid = models.CharField(max_length=250, unique=True)
    full_name = models.CharField(max_length=200)
    age = models.CharField(max_length=10)
    is_email_verified = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'gmail_uid', 'age', 'user_image']

    objects = CustomUserManager()

    def __str__(self):
        return self.full_name

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

class Vehicle(models.Model):

    VEHICLE_TYPE_MODEL = (
        ('SUV', 'SUV'),
        ('Jeep', 'Jeep'),
        ('sedan', 'Sedan'),
        ('convertile', 'Convertile'),
        ('mini_van', 'Mini_van'),
        ('crossover', 'Crossover'),
        ('sport_car', 'Sport_car'),
    )

    user = models.ForeignKey(CustomUser, related_name='user_vehicle', on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=30, choices=VEHICLE_TYPE_MODEL, default='sport_car')
    license_plate_number = models.CharField(max_length=50)
    car_model = models.CharField(max_length=100)

    def __str__(self):
        return self.car_model
