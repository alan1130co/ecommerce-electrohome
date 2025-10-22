from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    # Cambiado 'username' por 'email' porque tu modelo usa email como login
    list_display = ('email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff', 'fecha_registro')
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser', 'is_active', 'fecha_registro')
    search_fields = ('email', 'first_name', 'last_name', 'telefono')
    ordering = ('-fecha_registro',)
    
    fieldsets = (
        ('Información de Autenticación', {
            'fields': ('email', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'telefono')
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad', 'codigo_postal')
        }),
        ('Permisos', {
            'fields': ('tipo_usuario', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'fecha_registro'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Crear Usuario', {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'tipo_usuario'),
        }),
    )
    
    readonly_fields = ('last_login', 'fecha_registro')

admin.site.register(Usuario, UsuarioAdmin)
