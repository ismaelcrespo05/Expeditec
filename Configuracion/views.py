from django.shortcuts import render
from django.views import View
from django.http import HttpRequest
from Login import views as Login_views
from django.utils.html import escape
from verificacion_email import views as verificacion_views
from . import utils
from django.contrib.auth import authenticate, login as auth_login
from django.utils import timezone
from user_agents import parse
from django.contrib.sessions.models import Session
from django.utils.dateparse import parse_datetime

from Administrador import models as Admin_models
from RRHH import models as RRHH_models
# Create your views here.


def get_base(request):
    if request.user.is_staff:
        return "Admin/admin_base.html"
    try:
        aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
        return "Aspirante/aspirante_base.html"
    except Exception as e:
        pass

    try:
        rrhh = Admin_models.RRHH.objects.get(userid=request.user)
        return "RRHH/rrhh_base.html"
    except Exception as e:
        pass

def get_tribunales(request):
    try:
        aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
        return RRHH_models.Miembro_tribunal.objects.filter(miembro=aspirante)
    except Exception as e:
        return None

class Configuracion(View):
    @staticmethod
    def Notificacion(request:HttpRequest,Error=None,Success=None):
        if request.user.is_authenticated:
            sesiones = Configuracion.obtener_sesiones_activas(request)
            return render(request,'Configuracion/configuracion.html',{
                'Configuracion':True,
                'Error':Error,'Success':Success,
                'sesiones':sesiones,'sesion_actual':request.session.session_key,
                'base':get_base(request),
                'tribunales':get_tribunales(request),
            })
        else:
            return Login_views.redirigir_usuario(request=request)


    def get(self,request:HttpRequest):
        if request.user.is_authenticated:
            sesiones = Configuracion.obtener_sesiones_activas(request)
            return render(request,'Configuracion/configuracion.html',{
                'Configuracion':True,
                'sesiones':sesiones,'sesion_actual':request.session.session_key,
                'base':get_base(request),
                'tribunales':get_tribunales(request),
            })
        else:
            return Login_views.redirigir_usuario(request=request)


    def post(self,request:HttpRequest):
        if request.user.is_authenticated:
            return Configuracion.Notificacion(request=request)
        return Login_views.redirigir_usuario(request=request)




    @staticmethod
    def obtener_sesiones_activas(request):
        """
        Obtiene todas las sesiones activas con detalles del dispositivo.
        
        Args:
            request: HttpRequest (para obtener la sesión actual)
        
        Returns:
            list: Lista de diccionarios con información de cada sesión activa.
        """
        sesiones = Session.objects.filter(expire_date__gte=timezone.now())
        sesiones_activas = []
        
        for sesion in sesiones:
            try:
                datos_sesion = sesion.get_decoded()
                
                # Verificar que la sesión pertenece a un usuario autenticado
                if '_auth_user_id' not in datos_sesion or str(datos_sesion['_auth_user_id']) != str(request.user.pk):
                    continue    

                # Obtener información guardada
                device_info = datos_sesion.get('device_info', {})
                user_agent_str = datos_sesion.get('user_agent', '')
                
                # Si no hay device_info pero sí user_agent, parsearlo
                if not device_info and user_agent_str:
                    ua = parse(user_agent_str)
                    device_info = {
                        'navegador': ua.browser.family,
                        'version': ua.browser.version_string,
                        'sistema_operativo': ua.os.family,
                        'dispositivo': 'Móvil' if ua.is_mobile else 
                                      'Tablet' if ua.is_tablet else 
                                      'Computadora' if ua.is_pc else 
                                      'Bot' if ua.is_bot else 'Desconocido'
                    }
                
                # Si no hay nada, usar valores por defecto
                if not device_info:
                    device_info = {
                        'navegador': 'Desconocido',
                        'version': '',
                        'sistema_operativo': 'Desconocido',
                        'dispositivo': 'Desconocido'
                    }
                
                sesiones_activas.append({
                    'session_key': sesion.session_key,
                    'user_id': datos_sesion.get('_auth_user_id'),
                    'ip': datos_sesion.get('ip_address', 'Desconocida'),
                    'navegador': f"{device_info.get('navegador')} {device_info.get('version', '')}".strip(),
                    'so': device_info.get('sistema_operativo', 'Desconocido'),
                    'dispositivo': device_info.get('dispositivo', 'Desconocido'),
                    'login_time': timezone.localtime(parse_datetime(datos_sesion.get('login_time', ''))).strftime('%Y-%m-%d %H:%M:%S'),
                    'es_actual': (sesion.session_key == request.session.session_key)
                })
            except Exception as e:
                # Puedes loggear el error si es necesario
                print(e)
                continue
        
        return sesiones_activas










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





def cerrar_sesion_remota(request:HttpRequest):
    if request.POST and request.user.is_authenticated:
        session_key = request.POST.get('session_key')
        if session_key != request.session.session_key:
            Session.objects.filter(session_key=session_key).delete()
            return Configuracion.Notificacion(request=request,Success="Sesion cerrada correctamente.")
        return Configuracion.Notificacion(request=request,Error='Error, no se puede cerrar la sesion actual.')
    else:
        return Configuracion.Notificacion(request=request)
    
def cerrar_todas_las_sesiones(request:HttpRequest):
    if request.POST and request.user.is_authenticated:
        sesiones = Configuracion.obtener_sesiones_activas(request=request)
        i = 0
        for sesion in sesiones:
            if sesion.get('session_key') != request.session.session_key:
                Session.objects.filter(session_key=sesion.get('session_key')).delete()
                i+=1
        if i>0:
            return Configuracion.Notificacion(request=request,Success="Se han cerrado todas las sesiones correctamente")
        else:
            return Configuracion.Notificacion(request=request,Error="No hay sesiones por cerrar.")
    else:
        return Configuracion.Notificacion(request=request)