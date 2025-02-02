from .base import *

DEBUG = False

ADMINS = [
    ('Praise Idowu', 'ifeoluwapraise02@gmail.com'),
]

# ALLOWED_HOSTS = ['.vercel.app', '.now.sh'] 
ALLOWED_HOSTS = ['*'] 

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "db",
        "PORT": config("POSTGRES_PORT"),
    }
}

CELERY_BROKER_URL = 'redis://redis:6379/1'