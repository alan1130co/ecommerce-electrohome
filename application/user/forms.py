from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=100, required=True)
    email = forms.EmailField(label='Correo electrónico', required=True)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'email', 'telefono', 'password1', 'password2']