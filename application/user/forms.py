from django import forms
from .models import Usuario
import re

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )

    class Meta:
        model = Usuario
        fields = ['email', 'first_name', 'last_name', 'telefono']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+57 3001234567'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError("El nombre es obligatorio.")
        # Solo letras y espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', first_name):
            raise forms.ValidationError("El nombre solo puede contener letras y espacios.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError("El apellido es obligatorio.")
        # Solo letras y espacios
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', last_name):
            raise forms.ValidationError("El apellido solo puede contener letras y espacios.")
        return last_name

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Eliminar espacios y guiones
            telefono_limpio = telefono.replace(' ', '').replace('-', '')
            
            # Debe empezar con +57 y tener 10 dígitos después
            if not re.match(r'^\+57\d{10}$', telefono_limpio):
                raise forms.ValidationError("El teléfono debe tener el formato +57 seguido de 10 dígitos (ejemplo: +57 3001234567)")
            
            return telefono_limpio
        return telefono

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        # La contraseña debe ser encriptada
        user.set_password(self.cleaned_data['password1'])
        # El username se genera automáticamente en el método save() del modelo
        user.tipo_usuario = 'cliente'
        user.is_staff = False
        user.is_superuser = False
        
        if commit:
            user.save()
            # Agregar el backend para permitir login automático
            user.backend = 'django.contrib.auth.backends.ModelBackend'
        
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )