from .base import *
from decouple import config

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'

# ===== CONFIGURACIÓN CSRF PARA DESARROLLO =====
# Estas configuraciones solucionan el error "CSRF verification failed"
CSRF_COOKIE_SECURE = False  # No requiere HTTPS en desarrollo
CSRF_COOKIE_HTTPONLY = False  # Permite acceso JavaScript si es necesario
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000'
]

# ===== CONFIGURACIÓN DE SESIONES =====
SESSION_COOKIE_SECURE = False  # No requiere HTTPS en desarrollo
SESSION_COOKIE_SAMESITE = 'Lax'  # Permite cookies entre pestañas
CSRF_COOKIE_SAMESITE = 'Lax'  # Compatibilidad con navegadores modernos

# ===== CONFIGURACIÓN PARA DESARROLLO =====
# Estas líneas son útiles para debugging
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'  # Vista por defecto de error CSRF

# ===== CONFIGURACIÓN DE ARCHIVOS MEDIA (IMÁGENES) =====
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ===== CONFIGURACIÓN DE EMAIL PARA RECUPERACIÓN DE CONTRASEÑA =====
# Para desarrollo: Los emails se mostrarán en la consola del servidor
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Para producción con Gmail (descomenta cuando lo necesites):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='tu_email@gmail.com')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='tu_contraseña_app')
# DEFAULT_FROM_EMAIL = config('EMAIL_HOST_USER', default='tu_email@gmail.com')

# Configuración adicional para recuperación de contraseña
PASSWORD_RESET_TIMEOUT = 86400  # 24 horas en segundos (por defecto es 3 días)