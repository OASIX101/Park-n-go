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

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"