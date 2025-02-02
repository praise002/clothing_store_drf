from .base import *
from decouple import config

DEBUG = True

# ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(" ")
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ['https://*.ngrok.io', 'https://*.ngrok-free.app']


CSRF_TRUSTED_ORIGINS = ['https://*.ngrok.io', 'https://*.ngrok-free.app']

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT"),
    }
}

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'

# if DEBUG:
#     hide_toolbar_patterns = ["/media/", "/static/"]

#     DEBUG_TOOLBAR_CONFIG = {
#         "SHOW_TOOLBAR_CALLBACK": lambda request: not any(
#             request.path.startswith(p) for p in hide_toolbar_patterns
#         ),
#     }
