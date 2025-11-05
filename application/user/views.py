from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.cache import never_cache 
from .forms import RegisterForm, LoginForm

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('product:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Autenticar con email
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.email}!')
                return redirect('product:home')
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor verifica los datos del formulario.')
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})

@ensure_csrf_cookie
@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        return redirect('product:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Especificar el backend de autenticación
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'¡Bienvenido {user.first_name or user.email}! Tu cuenta ha sido creada 🎉')
            return redirect('product:home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegisterForm()

    return render(request, 'user/register.html', {'form': form})
 # ← esto evita el almacenamiento en caché de la vista
@never_cache 
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('user:login')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('user:login')

@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {'user': request.user})