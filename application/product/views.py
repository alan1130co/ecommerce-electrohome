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

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .cart_services import CartService
from application.order.order_services import OrderService
from .recommendations import get_recommendations_for_cart, RecommendationEngine

# ============================================================
# VIEWS DEL CARRITO (Agregar al final del archivo)
# ============================================================

def cart_view(request):
    """Vista del carrito de compras"""
    cart_service = CartService(request)
    cart_summary = cart_service.get_cart_summary()
    
    # Recomendaciones basadas en el carrito
    recommendations = []
    if cart_summary['items']:
        recommendations = get_recommendations_for_cart(cart_summary['items'], limit=4)
    
    context = {
        **cart_summary,
        'recommendations': recommendations,
    }
    
    return render(request, 'product/cart.html', context)


@require_POST
def add_to_cart(request, product_id):
    """Agregar producto al carrito (AJAX)"""
    try:
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({
                'success': False,
                'message': 'Cantidad inválida'
            }, status=400)
        
        cart_service = CartService(request)
        cart_item = cart_service.add_product(product_id, quantity)
        cart_summary = cart_service.get_cart_summary()
        
        return JsonResponse({
            'success': True,
            'message': f'{cart_item.product.nombre} agregado al carrito',
            'cart_total_items': cart_summary['total_items'],
            'cart_total': str(cart_summary['total']),
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error al agregar al carrito'
        }, status=500)


@require_POST
def update_cart_item(request, cart_item_id):
    """Actualizar cantidad de un item del carrito (AJAX)"""
    try:
        quantity = int(request.POST.get('quantity', 1))
        
        cart_service = CartService(request)
        cart_item = cart_service.update_quantity(cart_item_id, quantity)
        cart_summary = cart_service.get_cart_summary()
        
        if cart_item:
            return JsonResponse({
                'success': True,
                'message': 'Carrito actualizado',
                'item_subtotal': str(cart_item.subtotal),
                'cart_subtotal': str(cart_summary['subtotal']),
                'cart_tax': str(cart_summary['tax']),
                'cart_total': str(cart_summary['total']),
                'cart_total_items': cart_summary['total_items'],
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Producto eliminado',
                'cart_subtotal': str(cart_summary['subtotal']),
                'cart_tax': str(cart_summary['tax']),
                'cart_total': str(cart_summary['total']),
                'cart_total_items': cart_summary['total_items'],
            })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error al actualizar el carrito'
        }, status=500)


@require_POST
def remove_from_cart(request, cart_item_id):
    """Eliminar item del carrito (AJAX)"""
    try:
        cart_service = CartService(request)
        cart_service.remove_item(cart_item_id)
        cart_summary = cart_service.get_cart_summary()
        
        return JsonResponse({
            'success': True,
            'message': 'Producto eliminado del carrito',
            'cart_subtotal': str(cart_summary['subtotal']),
            'cart_tax': str(cart_summary['tax']),
            'cart_total': str(cart_summary['total']),
            'cart_total_items': cart_summary['total_items'],
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error al eliminar del carrito'
        }, status=500)


@require_POST
def clear_cart(request):
    """Vaciar el carrito (AJAX)"""
    try:
        cart_service = CartService(request)
        cart_service.clear_cart()
        
        return JsonResponse({
            'success': True,
            'message': 'Carrito vaciado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error al vaciar el carrito'
        }, status=500)

from django.db.models import Q

def search_view(request):
    """Vista de búsqueda de productos"""
    query = request.GET.get('q', '').strip()
    productos = []
    sugerencias = []
    
    if query:
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        ).filter(stock__gt=0, activo=True).select_related('categoria')
        
        # Sugerencias si no hay resultados
        if not productos.exists() and len(query) >= 3:
            sugerencias = Producto.objects.filter(
                nombre__istartswith=query[:3],
                activo=True,
                stock__gt=0
            ).select_related('categoria')[:6]
    
    context = {
        'productos': productos,
        'query': query,
        'total_results': productos.count() if productos else 0,
        'sugerencias': sugerencias,
    }
    
    return render(request, 'product/search_results.html', context)
def product_detail(request, product_id):
    """Vista de detalle del producto"""
    producto = get_object_or_404(Producto.objects.prefetch_related('galeria'), id=product_id)
    
    # Registrar la vista del producto para recomendaciones
    if request.user.is_authenticated:
        from .models import ProductView
        ProductView.objects.create(user=request.user, product=producto)
    
    # Obtener productos relacionados de la misma categoría
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        activo=True
    ).exclude(id=producto.id)[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    }
    
    return render(request, 'product/product_detail.html', context)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Min, Max

def products_list(request):
    """Vista de listado de productos con filtros y paginación"""
    
    # Obtener todos los productos activos
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    
    # FILTROS
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    # Filtro por búsqueda
    search_query = request.GET.get('q')
    if search_query:
        productos = productos.filter(
            Q(nombre__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    # Filtro por rango de precio
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)
    
    # Filtro por disponibilidad
    disponible = request.GET.get('disponible')
    if disponible == '1':
        productos = productos.filter(stock__gt=0)
    
    # Ordenamiento
    orden = request.GET.get('orden', '-fecha_creacion')
    orden_opciones = {
        'nombre_asc': 'nombre',
        'nombre_desc': '-nombre',
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'nuevo': '-fecha_creacion',
        'antiguo': 'fecha_creacion',
    }
    productos = productos.order_by(orden_opciones.get(orden, '-fecha_creacion'))
    
    # PAGINACIÓN
    paginator = Paginator(productos, 8)  # 8 productos por página
    page = request.GET.get('page', 1)
    
    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)
    
    # Obtener rango de precios para el filtro
    precio_range = Producto.objects.filter(activo=True).aggregate(
        min_precio=Min('precio'),
        max_precio=Max('precio')
    )
    
    # Obtener todas las categorías
    categorias = Categoria.objects.filter(activo=True)
    
    context = {
        'productos': productos_paginados,
        'categorias': categorias,
        'total_productos': paginator.count,
        'precio_range': precio_range,
        'filtros_activos': {
            'categoria': categoria_id,
            'search': search_query,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'disponible': disponible,
            'orden': orden,
        }
    }
    
    return render(request, 'product/products_list.html', context)

def contact(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Aquí puedes:
        # 1. Guardar en la base de datos
        # 2. Enviar un email
        # 3. Enviar notificación
        
        # Por ahora, solo mostramos un mensaje de éxito
        messages.success(request, '¡Gracias por contactarnos! Te responderemos pronto.')
        
        return redirect('product:contact')
    
    return render(request, 'product/contact.html')

