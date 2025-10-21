from django.contrib import admin
from .models import Categoria, Producto, ImagenProducto

# Inline para mostrar las imágenes dentro del producto
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ('imagen', 'descripcion', 'orden')

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'precio', 'stock', 'activo', 'disponible', 'fecha_creacion')
    list_filter = ('activo', 'categoria', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo', 'stock', 'precio')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    inlines = [ImagenProductoInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria', 'imagen_principal')
        }),
        ('Precio y Stock', {
            'fields': ('precio', 'stock', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)
    readonly_fields = ('fecha_creacion',)

class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'descripcion', 'orden')
    list_filter = ('producto',)
    search_fields = ('producto__nombre', 'descripcion')
    list_editable = ('orden',)

# Registrar modelos
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(ImagenProducto, ImagenProductoAdmin)