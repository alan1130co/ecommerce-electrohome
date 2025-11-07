# application/order/views.py
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from application.product.cart_services import CartService
from .order_services import OrderService
from .models import Order
from application.product.recommendations import RecommendationEngine


@login_required
def checkout_view(request):
    """Vista de checkout"""
    cart_service = CartService(request)
    cart_summary = cart_service.get_cart_summary()
    
    if not cart_summary['items']:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('product:cart')
    
    # Calcular envío estimado
    shipping_cost = 15000
    
    context = {
        **cart_summary,
        'shipping_cost': shipping_cost,
        'grand_total': cart_summary['total'] + shipping_cost,
    }
    
    return render(request, 'order/checkout.html', context)


@login_required
@require_POST
def process_checkout(request):
    """Procesar el checkout y crear la orden (AJAX)"""
    try:
        cart_service = CartService(request)
        cart = cart_service.get_or_create_cart()
        
        if not cart.items.exists():
            return JsonResponse({
                'success': False,
                'message': 'Tu carrito está vacío'
            }, status=400)
        
        order_data = {
            'email': request.POST.get('email', request.user.email),
            'phone': request.POST.get('phone'),
            'shipping_address': request.POST.get('shipping_address'),
            'shipping_city': request.POST.get('shipping_city'),
            'shipping_department': request.POST.get('shipping_department'),
            'shipping_postal_code': request.POST.get('shipping_postal_code', ''),
            'payment_method': request.POST.get('payment_method', 'credit_card'),
            'notes': request.POST.get('notes', ''),
        }
        
        # Validar campos requeridos
        required_fields = ['phone', 'shipping_address', 'shipping_city', 'shipping_department']
        for field in required_fields:
            if not order_data.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'El campo {field} es requerido'
                }, status=400)
        
        # Crear la orden
        order = OrderService.create_order_from_cart(request.user, cart, order_data)
        
        # Limpiar caché de recomendaciones
        engine = RecommendationEngine(user=request.user)
        engine.clear_user_cache()
        
        return JsonResponse({
            'success': True,
            'message': 'Orden creada exitosamente',
            'order_id': order.id,
            'order_number': order.order_number,
            'redirect_url': reverse('order:order_confirmation', kwargs={'order_id': order.id})  # ✅ CORREGIDO
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error al procesar la orden'
        }, status=500)
        
        # Crear la orden
        order = OrderService.create_order_from_cart(request.user, cart, order_data)
        
        # Limpiar caché de recomendaciones
        engine = RecommendationEngine(user=request.user)
        engine.clear_user_cache()
        
        return JsonResponse({
            'success': True,
            'message': 'Orden creada exitosamente',
            'order_id': order.id,
            'order_number': order.order_number,
            'redirect_url': f'/order/{order.id}/'
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error al procesar la orden'
        }, status=500)


@login_required
def order_confirmation(request, order_id):
    """Vista de confirmación de orden"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order/order_confirmation.html', {'order': order})


@login_required
def order_list(request):
    """Lista de órdenes del usuario"""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'order/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Detalle de una orden"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user
    )
    return render(request, 'order/order_detail.html', {'order': order})