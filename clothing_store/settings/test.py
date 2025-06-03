from .base import *

# Use a test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Use fast password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable Cloudinary uploads in tests
CLOUDINARY_URL = None

# Disable Celery tasks
CELERY_TASK_ALWAYS_EAGER = True