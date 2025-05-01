from django.shortcuts import render
from django.views import View
from django.http import HttpRequest
from Login import views as Login_views
from django.utils.html import escape
from verificacion_email import views as verificacion_views
from . import utils
from django.contrib.auth import authenticate, login as auth_login
# Create your views here.
class Configuracion(View):
    @staticmethod
    def Notificacion(request:HttpRequest,Error=None,Success=None):
        if request.user.is_authenticated:
            return render(request,'Configuracion/configuracion.html',{
                'Configuracion':True,
                'Error':Error,'Success':Success
            })
        else:
            return Login_views.redirigir_usuario(request=request)


    def get(self,request:HttpRequest):
        if request.user.is_authenticated:
            return render(request,'Configuracion/configuracion.html',{
                'Configuracion':True
            })
        else:
            return Login_views.redirigir_usuario(request=request)


    def post(self,request:HttpRequest):
        if request.user.is_authenticated:
            return Configuracion.Notificacion(request=request)
        return Login_views.redirigir_usuario(request=request)



class Cambiar_clave(View):
    def get(self,request:HttpRequest):
        if request.user.is_authenticated:
            return Configuracion.Notificacion(request)
        return Login_views.redirigir_usuario(request=request)
    
    def post(self,request:HttpRequest):
        if request.user.is_authenticated:
            tocken = escape(request.POST.get('verificationCode').strip())
            pass1 = escape(request.POST.get('pass1').strip())
            pass2 = escape(request.POST.get('pass2').strip())
            if verificacion_views.verificar_tocken(tocken=tocken,request=request):
                request.user.tocken = ""
                request.user.save()
                valid = utils.verificar_contraseñas(contraseña1=pass1,contraseña2=pass2)
                if valid=="OK":
                    request.user.set_password(pass1)
                    request.user.save()
                    user = authenticate(request, username=request.user.username, password=pass1)
                    auth_login(request, user)
                    return Configuracion.Notificacion(request=request,Success="Contraseña actualizada correctamente")
                else:
                    return Configuracion.Notificacion(request=request,Error=f"{valid}. Verifique nuevamente su correo electrónico.")
        return Login_views.redirigir_usuario(request=request)
