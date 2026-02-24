# subir_cloudinary.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'electrohome.Settings.local'  # ← usa tu BD local

import django
django.setup()

import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="dksen9swq",
    api_key="947537498923534",
    api_secret="g1rKC9K9knWn8g_OzLzyPCGv_UE"
)

from application.product.models import Producto, ImagenProducto

# Subir imagen principal
for producto in Producto.objects.all():
    if producto.imagen_principal and not str(producto.imagen_principal).startswith('http'):
        ruta_local = os.path.join('media', str(producto.imagen_principal))
        if os.path.exists(ruta_local):
            print(f'Subiendo: {producto.nombre}...')
            result = cloudinary.uploader.upload(ruta_local)
            producto.imagen_principal = result['secure_url']
            producto.save()
            print(f'✅ {producto.nombre} → {result["secure_url"]}')
        else:
            print(f'❌ No existe: {ruta_local}')

# Subir galería
for imagen in ImagenProducto.objects.all():
    if imagen.imagen and not str(imagen.imagen).startswith('http'):
        ruta_local = os.path.join('media', str(imagen.imagen))
        if os.path.exists(ruta_local):
            result = cloudinary.uploader.upload(ruta_local)
            imagen.imagen = result['secure_url']
            imagen.save()
            print(f'✅ Galería OK')
        else:
            print(f'❌ No existe: {ruta_local}')

print("\n✅ ¡Listo!")