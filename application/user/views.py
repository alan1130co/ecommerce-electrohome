from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .forms import RegisterForm, LoginForm

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('product:home')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        # ⚡ Importante: usamos username=email porque tu USERNAME_FIELD es email
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.email}!')
            return redirect('product:home')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'user/login.html', {'form': form})

@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        return redirect('product:home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'¡Bienvenido {user.first_name or user.email}! Tu cuenta ha sido creada 🎉')
        return redirect('product:home')
    elif request.method == 'POST':
        messages.error(request, 'Por favor corrige los errores en el formulario.')

    return render(request, 'user/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('user:login')

@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {'user': request.user})
