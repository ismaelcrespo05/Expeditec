from django.shortcuts import render
from django.views import View
from django.http import HttpRequest
from django.contrib.auth.models import User
from Login import views as Login_views
from Administrador import models as Admin_models
from . import models as Chat_models
from RRHH import models as RRHH_models
from Aspirante import models as Aspirante_models
# Create your views here.

class Open_Chat(View):
    def get(self, request: HttpRequest, chatid: int):
        # Verificación inicial rápida del tipo de usuario
        if request.user.tipo_usuario not in ["Aspirante", "RRHH"]:
            return Login_views.redirigir_usuario(request=request)

        try:
            

            # Optimización: Obtener solo el ID necesario de la solicitud
            solicitud = Aspirante_models.SolicitudCambioCategoria.objects.only('id').get(id=chatid)
            

            # Obtener el chat con relaciones precargadas
            chat = Chat_models.Chat.objects.select_related('solicitud_id').get(solicitud_id=solicitud.id)
            

            # Verificar membresía del usuario en el chat (consulta optimizada)
            if not Chat_models.Miembro_Chat.objects.filter(chat_id=chat.id, userid=request.user).exists():
                return Login_views.redirigir_usuario(request=request)

            # Obtener datos del aspirante actual (si existe) en una sola consulta
            aspirante = Admin_models.Aspirante.objects.filter(userid=request.user).select_related('userid').first()
            

            # Obtener todos los miembros del chat con sus usuarios relacionados
            miembros_chat = Chat_models.Miembro_Chat.objects.filter(
                chat_id=chat.id
            ).exclude(userid=request.user).order_by('-tipo')
            
            # Preparar datos para la plantilla
            return render(request, "Chat/chat.html", {
                'aspirante': aspirante,
                'chat_members': miembros_chat,
                'solicitud':solicitud,
                'WS_URL' : f"ws://{request.get_host()}/ws/chat/{solicitud.id}/"
            })

        except Exception as e:
            print(f"Error en chat view: {str(e)}")
            return Login_views.redirigir_usuario(request=request)
    def post(self,request):
        pass