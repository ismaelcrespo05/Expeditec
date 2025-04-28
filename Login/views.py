from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django_user_agents.utils import get_user_agent
from django.utils import timezone
from django.conf import settings
from django.http import HttpRequest
from django.views import View
from django.utils.html import escape
# Create your views here.



def redirigir_usuario(request:HttpRequest):
    """Función centralizada para redirigir según el tipo de usuario"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_staff:
        return redirect('admin_dashboard')
    # Aquí puedes añadir más roles según necesites
    # elif request.user.es_cliente:
    #     return redirect('cliente_dashboard')
    else:
        return redirect('dashboard_default')



class Login(View):
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
            return render(request, 'Login/login.html',{
                'Error':'Todos los campos son obligatorios.'
            })
        try:
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
                
            return render(request, 'Login/login.html',{
                'Error':"Credenciales incorrectas"
            })
            
            
        except Exception as e:
            # Log del error para debugging
            return render(request, 'Login/login.html',{
                'Error':f'Error del servidor: {str(e)}'
            })
            


class Logout(View):
    def get(self,request:HttpRequest):
        if request.user.is_authenticated:
            logout(request)
            return redirect("login")
        else:
            return redirigir_usuario(request)
        
    def post(self,request):
        return redirigir_usuario(request)
     
            