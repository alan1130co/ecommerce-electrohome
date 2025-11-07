# application/product/urls.py
from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # Home
    path('', views.index, name='home'),
    
    # Carrito
    path('carrito/', views.cart_view, name='cart'),
    path('carrito/agregar/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/actualizar/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('carrito/eliminar/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('carrito/vaciar/', views.clear_cart, name='clear_cart'),
    path('search/', views.search_view, name='search'),
]