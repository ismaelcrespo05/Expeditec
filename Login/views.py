from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django_user_agents.utils import get_user_agent
from django.utils import timezone
from django.conf import settings
from django.http import HttpRequest,HttpResponse, JsonResponse
from django.views import View
from django.utils.html import escape
from Administrador import models as Admin_models
from django.contrib.auth.models import User
from verificacion_email import views as verificacion_views
from Configuracion import utils as Config_utils
# Create your views here.



def redirigir_usuario(request:HttpRequest):
    """Función centralizada para redirigir según el tipo de usuario"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Aquí puedes añadir más roles según necesites
    try:
        aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
        return redirect('aspirante_dashboard')
    except Exception:
        pass

    try:
        rrhh = Admin_models.RRHH.objects.get(userid=request.user)
        return redirect('rrhh_dashboard')
    except Exception as e:
        pass
    #   return redirect('cliente_dashboard')
    


class Login(View):
    @staticmethod
    def Notificacion(request:HttpRequest,Error=None,Success=None):
        if request.user.is_authenticated:
            return redirigir_usuario(request)
        return render(request, 'Login/login.html',{
            'Error':Error,
            'Success':Success,
        })

    def get(self, request:HttpRequest):
        if request.user.is_authenticated:
            return redirigir_usuario(request)
        return render(request, 'Login/login.html')

    def post(self, request:HttpRequest):
        if request.user.is_authenticated:
            return redirigir_usuario(request)
            
        username = escape(request.POST.get('username'))
        password = escape(request.POST.get('password'))
        
        if not username or not password:
            return Login.Notificacion(request=request,Error="Todos los campos son obligatorios.")
        try:
            return Login.autenticar(request=request,username=username,password=password)
        except Exception as e:
            # Log del error para debugging
            return Login.Notificacion(request=request,Error=f'Error del servidor: {str(e)}')
    
    @staticmethod    
    def autenticar(request,username,password):
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            
            user_agent = get_user_agent(request)
            
            # Guardar información en la sesión
            request.session['user_agent'] = str(user_agent)
            request.session['ip_address'] = request.META.get('REMOTE_ADDR')
            request.session['login_time'] = timezone.now().isoformat()
            
            # También puedes guardar los datos parseados directamente
            request.session['device_info'] = {
                'navegador': user_agent.browser.family,
                'version': user_agent.browser.version_string,
                'sistema_operativo': user_agent.os.family,
                'dispositivo': 'Móvil' if user_agent.is_mobile else 
                            'Tablet' if user_agent.is_tablet else 
                            'Computadora' if user_agent.is_pc else 
                            'Bot' if user_agent.is_bot else 'Desconocido'
            }


            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            request.session.save()
            
            return redirigir_usuario(request=request)
        return Login.Notificacion(request=request,Error="Credenciales incorrectas")   
            

class Logout(View):
    def get(self,request:HttpRequest):
        if request.user.is_authenticated:
            logout(request)
            return redirect("login")
        else:
            return redirigir_usuario(request)
        
    def post(self,request):
        return redirigir_usuario(request)
     




class Cambio_clave(View):
    @staticmethod
    def Notificacion(request:HttpRequest,Error=None,Success=None,step=None,username=None,code=None):
        if not request.user.is_authenticated:
            return render(request, f'Login/cambio_clave_{step}.html',{
                'Error':Error,'Success':Success,'username':username,'code':code
            })
        else:
            return redirigir_usuario(request)
        
    def get(self,request:HttpRequest):
        if not request.user.is_authenticated:
            return render(request, 'Login/cambio_clave_1.html')
        else:
            return redirigir_usuario(request)
        

    def post(self,request:HttpRequest):
        if not request.user.is_authenticated:
            opc = request.POST.get('opc')
            if opc == 'username':
                username = escape(request.POST.get('username'))
                userid = None
                try:
                    userid = User.objects.get(username=username)
                except Exception as e:
                    return Cambio_clave.Notificacion(request=request,Error="El usuario no existe.",step=1)
                
                try:
                    verificacion_views.Enviar_tocken_unauthenticated(request,userid=userid)
                    #Aqui retorno al paso 2
                    return Cambio_clave.Notificacion(request=request,step=2,username=username)
                except Exception as e:
                    return Cambio_clave.Notificacion(request=request,Error="Error al enviar codigo de confirmacion vuela a intentar.",step=1)
            else:
                username = escape(request.POST.get('username'))
                userid = None
                try:
                    userid = User.objects.get(username=username)
                except Exception as e:
                    return Cambio_clave.Notificacion(request=request,Error="El usuario no existe.",step=1)
                
                if opc=="reenviar_code":
                    try:
                        verificacion_views.Enviar_tocken_unauthenticated(request,userid=userid)
                    except Exception as e:
                        return Cambio_clave.Notificacion(request=request,Error="Error al reenviar codigo de confirmacion vuela a intentar.",step=2,username=username)
                    #Aqui retorno al paso 2
                    return Cambio_clave.Notificacion(request=request,step=2,username=username,Success="Codigo de verificacion reenviado correctamente.")
                else:
                    code = escape(request.POST.get('verificationCode'))
                    if code == userid.tocken:
                        if opc=="code":
                            return Cambio_clave.Notificacion(request=request,step=3,username=username,code=code,Success="Codigo de confirmacion correcto. Inserte su nueva clave.")
                        elif opc=="cambiar_clave":
                            pass1 = escape(request.POST.get('pass1'))
                            pass2 = escape(request.POST.get('pass2'))
                            valid = Config_utils.verificar_contraseñas(pass1,pass2)
                            if valid == 'OK':
                                userid.set_password(pass1)
                                userid.save()
                                return Login.Notificacion(request=request,Success="Contraseña cambiada correctamente.")
                            else:
                                return Cambio_clave.Notificacion(request=request,Error=valid,step=3,username=username,code=code)
            
                    else:
                        return Cambio_clave.Notificacion(request=request,Error="El codigo no es correcto.",step=2,username=username)
        else:
            return redirigir_usuario(request)