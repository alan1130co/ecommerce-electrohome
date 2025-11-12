from .base import *
from decouple import config
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# ===== CONFIGURACIÓN DE BASE DE DATOS POSTGRESQL =====
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='esenciakr_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# ===== CONFIGURACIÓN DE CACHÉ PARA RECOMENDACIONES (DESARROLLO) =====
# Opción 1: Caché en memoria local (NO REQUIERE REDIS - Fácil para desarrollo)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'electrohome-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Opción 2: Redis (DESCOMENTA si instalaste Redis para mejor performance)
# Instalar: pip install django-redis redis
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'IGNORE_EXCEPTIONS': True,  # No romper la app si Redis falla
#         },
#         'KEY_PREFIX': 'electrohome_dev',
#         'TIMEOUT': 3600,
#     }
# }

# Configuración de timeouts de caché para recomendaciones
RECOMMENDATION_CACHE_TIMEOUT = 3600  # 1 hora
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutos

# ===== CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS =====
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ===== CONFIGURACIÓN DE ARCHIVOS MEDIA (IMÁGENES) =====
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ===== CONFIGURACIÓN CSRF PARA DESARROLLO =====
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000'
]

# ===== CONFIGURACIÓN DE SESIONES =====
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = False

# ===== CONFIGURACIÓN PARA DESARROLLO =====
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# ===== CONFIGURACIÓN DE EMAIL =====
# Para desarrollo (muestra emails en consola)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Para producción con Gmail (ACTIVAR ESTO)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # Leer desde .env
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # Leer desde .env
DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER')
SERVER_EMAIL = config('EMAIL_HOST_USER')

PASSWORD_RESET_TIMEOUT = 86400  # 24 horas
# Para producción con Gmail (descomenta cuando lo necesites):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='tu_email@gmail.com')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='tu_contraseña_app')
# DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER', default='tu_email@gmail.com')

PASSWORD_RESET_TIMEOUT = 86400  # 24 horas

# ===== CONFIGURACIÓN DE RECOMENDACIONES =====
RECOMMENDATION_CONFIG = {
    'CACHE_TIMEOUT': 3600,  # 1 hora
    'MIN_RATINGS_FOR_BEST_RATED': 3,
    'GLOBAL_AVERAGE_RATING': 3.5,
    'SIMILAR_USERS_LIMIT': 20,
    'TRENDING_DAYS': 7,
    'POPULAR_DAYS': 30,
    'VIEW_DUPLICATE_THRESHOLD_MINUTES': 5,
}

# ===== LOGGING PARA DEBUGGING =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'application': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Ver queries SQL (útil para optimizar)
        },
    },
}

# ===== DJANGO DEBUG TOOLBAR (OPCIONAL - MUY ÚTIL) =====
# Instalar: pip install django-debug-toolbar
# Descomentar para activar:
"""
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
INTERNAL_IPS = ['127.0.0.1']

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    'SHOW_COLLAPSED': True,
}
"""

# Configuración de allauth para Google
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_STORE_TOKENS = True