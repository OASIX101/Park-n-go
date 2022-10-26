from .base import *
from Hackathon.settings import base

DEBUG = True
ALLOWED_HOSTS = []


INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE = base.MIDDLEWARE + [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INSTALLED_APPS = base.INSTALLED_APPS + [
    'debug_toolbar',
]

EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmass.co'
EMAIL_PORT = 465
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"