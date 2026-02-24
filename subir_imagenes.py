import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'electrohome.Settings.local'

import django
django.setup()

import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="dksen9swq",
    api_key="947537498923534",       # <- pon tu API Key
    api_secret="g1rKC9K9knWn8g_OzLzyPCGv_UE"  # <- pon tu API Secret
)

from application.product.models import Producto, ImagenProducto

# Subir imagen principal de cada producto
print("=== Subiendo imágenes principales ===")
for producto in Producto.objects.all():
    if producto.imagen_principal:
        ruta_local = os.path.join('media', str(producto.imagen_principal))
        if os.path.exists(ruta_local):
            print(f'Subiendo: {producto.nombre}...')
            result = cloudinary.uploader.upload(ruta_local)
            producto.imagen_principal = result['secure_url']
            producto.save()
            print(f'✅ {producto.nombre}')
        else:
            print(f'❌ No existe: {ruta_local}')

# Subir galería de imágenes
print("\n=== Subiendo galería de imágenes ===")
for imagen in ImagenProducto.objects.all():
    if imagen.imagen:
        ruta_local = os.path.join('media', str(imagen.imagen))
        if os.path.exists(ruta_local):
            print(f'Subiendo galería: {ruta_local}...')
            result = cloudinary.uploader.upload(ruta_local)
            imagen.imagen = result['secure_url']
            imagen.save()
            print(f'✅ OK')
        else:
            print(f'❌ No existe: {ruta_local}')

print("\n✅ ¡Listo! Todas las imágenes subidas a Cloudinary.")