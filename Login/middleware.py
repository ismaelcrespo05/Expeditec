# Crea un nuevo archivo middleware.py en tu app Login
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpRequest
class SessionExpiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request:HttpRequest):
        response = self.get_response(request)
        excepto = [
            reverse('login'),
            reverse('recuperar_clave'),
            reverse('enviar_token'),
            reverse('registro'),
        ]
        # Verificar si la sesión expiró y el usuario no está autenticado
        if not request.user.is_authenticated and not request.path in excepto:    
            return redirect(reverse('login'))
        
        return response