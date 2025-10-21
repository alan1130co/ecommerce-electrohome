from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff', 'fecha_registro')
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser', 'is_active', 'fecha_registro')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'telefono')
    ordering = ('-fecha_registro',)
    
    fieldsets = (
        ('Información de Autenticación', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono')
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad', 'codigo_postal')
        }),
        ('Permisos', {
            'fields': ('tipo_usuario', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'fecha_registro'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Crear Usuario', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'tipo_usuario'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'fecha_registro')

# Registrar modelo
admin.site.register(Usuario, UsuarioAdmin)