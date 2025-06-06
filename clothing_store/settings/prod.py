from datetime import timedelta

from .base import *

DEBUG = False

ADMINS = [
    ("Praise Idowu", "ifeoluwapraise02@gmail.com"),
]

# ALLOWED_HOSTS = ['.vercel.app', '.now.sh']
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "db",
        "PORT": config("POSTGRES_PORT"),
    }
}

CELERY_BROKER_URL = "redis://redis:6379/1"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=60
    ),  # Short-lived access tokens for production
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "SIGNING_KEY": config("JWT_SECRET_KEY"),
}

CORS_ALLOWED_ORIGINS = [
    config("FRONTEND_URL_PROD"),
]

FRONTEND_URL = config("FRONTEND_URL_PROD")
FRONTEND_URL = config("FRONTEND_URL_PROD")
