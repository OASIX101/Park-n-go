from .base import *
from Hackathon.settings import base

DEBUG = False

ALLOWED_HOSTS = ['Park-n-Go.herokuapp.com']

INSTALLED_APPS = base.INSTALLED_APPS + [
    'cloudinary',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'd84bei8buppmau',
        'USER': 'hxtshipeqmkuxq',
        'PASSWORD': 'f1bb1a5cf0f07a1e6b825dad7fcd040f34ba1930359b74bbda86e223128cb0ad',
        'HOST': 'ec2-52-200-5-135.compute-1.amazonaws.com',
        'PORT': '5432',
    }
}

EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmass.co'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUD_NAME'),
    'API_KEY': os.getenv('API_KEY'),
    'API_SECRET': os.getenv('API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"