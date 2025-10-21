from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class Usuario(AbstractUser):
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=[
            ('cliente', 'Cliente'),
            ('admin', 'Administrador'),
        ],
        default='cliente'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Sobrescribir los campos para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='grupos',
        blank=True,
        help_text='Los grupos a los que pertenece este usuario.',
        related_name='usuarios',
        related_query_name='usuario',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='permisos de usuario',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        related_name='usuarios',
        related_query_name='usuario',
    )

    def __str__(self):
        return self.username
    
    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']