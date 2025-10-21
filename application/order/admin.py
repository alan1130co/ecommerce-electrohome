from django.contrib import admin
from .models import Pedido, DetallePedido

# Inline para mostrar los detalles dentro del pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    readonly_fields = ('subtotal',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_pedido', 'estado', 'total')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('usuario__username', 'usuario__email', 'id')
    list_editable = ('estado',)
    readonly_fields = ('fecha_pedido', 'total')
    inlines = [DetallePedidoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('usuario', 'estado', 'fecha_pedido')
        }),
        ('Detalles de Envío', {
            'fields': ('direccion_envio', 'notas')
        }),
        ('Total', {
            'fields': ('total',),
            'description': 'El total se calcula automáticamente.'
        }),
    )

class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('pedido__estado', 'producto')
    search_fields = ('producto__nombre', 'pedido__id', 'pedido__usuario__username')
    readonly_fields = ('subtotal',)

# Registrar modelos
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(DetallePedido, DetallePedidoAdmin)