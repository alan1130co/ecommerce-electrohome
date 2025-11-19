# ============================================
# application/user/views.py
# SOLUCIÓN COMPLETA PARA LOGOUT
# ============================================

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from .forms import RegisterForm, LoginForm

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('product:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.email}!')
                
                # Redirigir al 'next' si existe, sino al home
                next_url = request.GET.get('next', 'product:home')
                return redirect(next_url)
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
    """Vista de registro"""
    if request.user.is_authenticated:
        return redirect('product:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'¡Bienvenido {user.first_name or user.email}! Tu cuenta ha sido creada 🎉')
            return redirect('product:home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegisterForm()

    return render(request, 'user/register.html', {'form': form})


# ============================================
# ✅ SOLUCIÓN COMPLETA PARA LOGOUT
# ============================================

@never_cache  # Evita caché del navegador
@login_required(login_url='user:login')  # Solo usuarios autenticados
@require_http_methods(["GET", "POST"])  # Acepta GET y POST
def logout_view(request):
    """
    Cierra la sesión del usuario y redirige al home.
    
    Comportamiento:
    - Cierra sesión correctamente
    - Limpia la caché del navegador
    - Redirige al home (el usuario puede seguir navegando)
    - Muestra mensaje de confirmación
    """
    # Obtener el nombre del usuario antes de cerrar sesión
    user_name = request.user.first_name or request.user.username
    
    # Cerrar sesión
    logout(request)
    
    # Mensaje de confirmación
    messages.success(request, f'¡Hasta pronto, {user_name}! Has cerrado sesión correctamente.')
    
    # ✅ REDIRIGIR AL HOME (no al login)
    # El usuario puede seguir navegando sin iniciar sesión
    return redirect('product:home')


@login_required
@never_cache
def profile_view(request):
    """Vista del perfil del usuario"""
    return render(request, 'user/profile.html', {'user': request.user})


@login_required
@never_cache
def edit_profile(request):
    """Editar perfil del usuario"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        
        if not user.email:
            messages.error(request, 'El email es obligatorio')
            return redirect('user:edit_profile')
        
        user.save()
        messages.success(request, '¡Perfil actualizado correctamente! ✅')
        return redirect('user:profile')
    
    return render(request, 'user/edit_profile.html', {'user': request.user})


# ============================================
# OPCIONAL: Vista para manejar acceso denegado
# ============================================

@never_cache
def access_denied(request):
    """
    Página mostrada cuando un usuario no autenticado
    intenta acceder a una página protegida
    """
    messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
    return redirect('user:login')