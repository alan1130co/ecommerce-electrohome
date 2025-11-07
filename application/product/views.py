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
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        ).filter(stock__gt=0)
    
    context = {
        'products': products,
        'query': query,
        'total_results': products.count()
    }
    
    return render(request, 'product/search_results.html', context)

