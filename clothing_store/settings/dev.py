from .base import *
from decouple import config
from django.utils.log import DEFAULT_LOGGING
import logging
import logging.config

DEBUG = True

# ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(" ")
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://*.ngrok.io", "https://*.ngrok-free.app"]


CSRF_TRUSTED_ORIGINS = ["https://*.ngrok.io", "https://*.ngrok-free.app"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": config("POSTGRES_HOST"),
        "PORT": config("POSTGRES_PORT"),
    }
}

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"

# if DEBUG:
#     hide_toolbar_patterns = ["/media/", "/static/"]

#     DEBUG_TOOLBAR_CONFIG = {
#         "SHOW_TOOLBAR_CALLBACK": lambda request: not any(
#             request.path.startswith(p) for p in hide_toolbar_patterns
#         ),
#     }

logger = logging.getLogger(__name__)
LOG_LEVEL = "INFO"
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            },
            "file": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"},
            "django.server": DEFAULT_LOGGING["formatters"]["django.server"],
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "file",
                "filename": "logs/clothing_store.log",
                "maxBytes": 10485760,  # 10 MB
                "backupCount": 5,  # Keep up to 5 backup files
            },
            "django.server": DEFAULT_LOGGING["handlers"]["django.server"],
        },
        "loggers": {
            "": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "apps": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
        },
    }
)
