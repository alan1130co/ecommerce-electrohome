from .base import *
import os
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')

EMAIL_BACKEND = 'anymail.backends.resend.EmailBackend'
ANYMAIL = {
    'RESEND_API_KEY': os.environ.get('RESEND_API_KEY', ''),
}
DEFAULT_FROM_EMAIL = 'onboarding@resend.dev'

WOMPI_PUBLIC_KEY = os.environ.get('WOMPI_PUBLIC_KEY', '')
WOMPI_PRIVATE_KEY = os.environ.get('WOMPI_PRIVATE_KEY', '')
WOMPI_ENVIRONMENT = os.environ.get('WOMPI_ENVIRONMENT', 'test')
WOMPI_API_URL = 'https://sandbox.wompi.co/v1'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ===== CLOUDINARY =====
INSTALLED_APPS += ['cloudinary_storage', 'cloudinary', 'anymail']

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}