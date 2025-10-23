from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('order/', include('application.order.urls')),
    path('user/', include('application.user.urls')),
    path('', include('application.product.urls')),  # ← CAMBIADO: sin tupla
]

# Archivos multimedia
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)