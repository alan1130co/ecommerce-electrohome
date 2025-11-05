from django.shortcuts import render
from django.views.decorators.cache import never_cache 
from .models import Producto, Categoria


@never_cache 
def index(request):
    """
    Vista principal del home de la tienda.
    """
    # Obtener todos los productos activos
    productos = Producto.objects.filter(activo=True)
    
    # Obtener categorías para filtros (opcional)
    categorias = Categoria.objects.filter(activo=True)
    
    # Productos por categoría (ajusta los nombres según tus categorías reales)
    productos_cocina = productos.filter(categoria__nombre__icontains='cocina')[:15]
    productos_limpieza = productos.filter(categoria__nombre__icontains='limpieza')[:15]
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'productos_cocina': productos_cocina,
        'productos_limpieza': productos_limpieza,
    }
    
    return render(request, 'product/home.html', context)