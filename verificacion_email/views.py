from django.shortcuts import render
from django.views import View
from django.http import HttpRequest,HttpResponse
from Login import views as Login_views
from Administrador import utils
from . import correo
from django.contrib.auth.models import User
from django.utils.html import escape
from datetime import datetime
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

Hemos recibido solicitud que requiere verificar su identidad en su cuente en Expeditec. 

Tu código de verificación es: 

{tocken}

Si no has solicitado este cambio, por favor ignora este mensaje o contacta al equipo de soporte inmediatamente.

Atentamente,
Equipo de Soporte Técnico
Expeditec

---
© {datetime.now().year} Expeditec. Todos los derechos reservados.
Este es un correo automático, por favor no respondas directamente.
"""
            correo.enviar_correo(email=request.user.email,asunto=Asunto,mensaje=mail)
            return HttpResponse("Todo está correcto", status=200)
        else:
            return Login_views.redirigir_usuario(request)
    def post(self,request:HttpRequest):
        return Login_views.redirigir_usuario(request)
    









def Enviar_tocken_unauthenticated(request:HttpRequest,userid:User):

    tocken=utils.generar_contraseña(longitud=10)
    userid.tocken = escape(tocken)
    userid.save()

    Asunto = "Confirmación de identidad requerida"
    mail = f"""
Hola {userid.username},

Hemos recibido solicitud que requiere verificar su identidad en su cuente en Expeditec. 

Tu código de verificación es: 

{tocken}

Si no has solicitado este cambio, por favor ignora este mensaje o contacta al equipo de soporte inmediatamente.

Atentamente,
Equipo de Soporte Técnico
Expeditec

---
© {datetime.now().year} Expeditec. Todos los derechos reservados.
Este es un correo automático, por favor no respondas directamente.
"""
    correo.enviar_correo(email=userid.email,asunto=Asunto,mensaje=mail)
    
        




def verificar_tocken (tocken,request):
    return request.user.tocken == tocken
    