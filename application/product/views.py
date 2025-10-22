from django.shortcuts import render

def index(request):
    """
    Vista principal del home de la tienda.
    """
    return render(request, 'product/home.html')
