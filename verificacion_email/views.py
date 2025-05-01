from django.shortcuts import render
from django.views import View
from django.http import HttpRequest,HttpResponse
from Login import views as Login_views
from Administrador import utils
from . import correo
# Create your views here.

class Enviar_tocken(View):
    def get(self, request:HttpRequest):
        if request.user.is_authenticated:
            tocken=utils.generar_contraseña(longitud=10)
            request.user.tocken = tocken
            request.user.save()
            Asunto = "Confirmación de identidad requerida"
            mail = f"""
Hola {request.user.username},

Hemos recibido solicitud que requiere verificar su identidad de su cuente en Expeditec. 

Tu código de verificación es: 

{tocken}

Si no has solicitado este cambio, por favor ignora este mensaje o contacta al equipo de soporte inmediatamente.

Atentamente,
Equipo de Soporte Técnico
Expeditec

---
© 2025 Expeditec. Todos los derechos reservados.
Este es un correo automático, por favor no respondas directamente.
"""
            correo.enviar_correo(email=request.user.email,asunto=Asunto,mensaje=mail)
            return HttpResponse("Todo está correcto", status=200)
        else:
            return Login_views.redirigir_usuario(request)
    def post(self,request:HttpRequest):
        return Login_views.redirigir_usuario(request)
    



def verificar_tocken (tocken,request):
    return request.user.tocken == tocken
    