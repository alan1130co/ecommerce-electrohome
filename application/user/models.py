from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crea y guarda un usuario regular"""
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        
        # Generar username automáticamente si no se proporciona
        if 'username' not in extra_fields or not extra_fields.get('username'):
            import uuid
            base_username = email.split('@')[0]
            extra_fields['username'] = f"{base_username}_{uuid.uuid4().hex[:8]}"
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crea y guarda un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('tipo_usuario', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    # Email como campo único y obligatorio
    email = models.EmailField(unique=True, blank=False)
    
    # Username opcional (se genera automáticamente)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
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
    
    # Configurar email como campo de login principal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Usar el manager personalizado
    objects = UsuarioManager()
    
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
    
    def save(self, *args, **kwargs):
        # Generar username automáticamente si no existe
        if not self.username:
            import uuid
            base_username = self.email.split('@')[0]
            self.username = f"{base_username}_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
    
    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']


# Proxy Model para Administradores
class Administrador(Usuario):
    class Meta:
        proxy = True
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
        app_label = 'auth'  # Esto lo pondrá en AUTHENTICATION AND AUTHORIZATION


# Proxy Model para Clientes
class Cliente(Usuario):
    class Meta:
        proxy = True
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'