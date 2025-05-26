from django.shortcuts import render
from django.views import View
from Login import views as Login_views
from Administrador import models as Admin_models,utils as Admin_utils
from django.http import HttpRequest

from Chat import models as Chat_models
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from Aspirante import models as Aspirante_models
from RRHH import models as RRHH_models

# Create your views here.



class RRHH_Dashboard(View):
    def get(self,request):
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
            cant_profesores = Admin_models.Aspirante.objects.filter(tipo='Profesor').count()
            cant_estudiantes = Admin_models.Aspirante.objects.filter(tipo='Estudiante').count()
            cantidad_x_categoria = Admin_utils.contar_por_categoria_docente()
            total_usuarios = cant_estudiantes + cant_profesores
            distribucion_x_categoria = {}
            for categoria, cantidad in cantidad_x_categoria.items():
                distribucion_x_categoria[categoria] = round((cantidad / total_usuarios) * 100, 2) if total_usuarios != 0 else 0
            
            return render(request,'RRHH/dashboard.html',{
                'rrhh':rrhh,
                'Dashboard':True,'cant_profesores':cant_profesores,'cant_estudiantes':cant_estudiantes,
                'total_personal':total_usuarios,'cantidad_x_categoria':cantidad_x_categoria,
                'distribucion_x_categoria':distribucion_x_categoria
            })
        
        except Exception as e:
            return Login_views.redirigir_usuario(request=request)

    def post(self,request):
        pass






class Solicitudes(View):
    @staticmethod
    def Notificacion(request, Error=None, Success=None):
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
            
            solicitudes = Aspirante_models.SolicitudCambioCategoria.objects.all().order_by('-fecha_solicitud')
            
            ESTADOS = Aspirante_models.ESTADOS
            CATEGORIAS = Admin_models.CATEGORIA_DOCENTE_CHOICES
            
            solicitudes_por_estado = {
                estado: solicitudes.filter(estado=estado) 
                for estado in ESTADOS
            }
            
            total_solicitudes = solicitudes.count()
            tiene_solicitudes_activas = solicitudes.filter(estado__in=['Pendiente', 'En revisión']).exists()

            return render(request, 'RRHH/solicitudes.html', {
                "Cambio_categoria": True,
                "solicitudes_por_estado": solicitudes_por_estado,
                "estados_filtro": ESTADOS,
                "categorias_filtro": CATEGORIAS,
                "total_solicitudes": total_solicitudes,
                "puede_solicitar": not tiene_solicitudes_activas,
                'rrhh': rrhh,
                'Solicitudes': True,
                'CARGOS_CHOICES': ['Presidente','Secretario'],
                'Error':Error,'Success':Success
            })
        except Exception as e:
            print(e)
            return Login_views.redirigir_usuario(request=request)

    def get(self, request: HttpRequest):
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
            
            solicitudes = Aspirante_models.SolicitudCambioCategoria.objects.all().order_by('-fecha_solicitud')
            
            ESTADOS = Aspirante_models.ESTADOS
            CATEGORIAS = Admin_models.CATEGORIA_DOCENTE_CHOICES

            solicitudes_por_estado = {
                estado: solicitudes.filter(estado=estado) 
                for estado in ESTADOS
            }
            
            total_solicitudes = solicitudes.count()
            tiene_solicitudes_activas = solicitudes.filter(estado__in=['Pendiente', 'En revisión']).exists()

            return render(request, 'RRHH/solicitudes.html', {
                "Cambio_categoria": True,
                "solicitudes_por_estado": solicitudes_por_estado,
                "estados_filtro": ESTADOS,
                "categorias_filtro": CATEGORIAS,
                "total_solicitudes": total_solicitudes,
                "puede_solicitar": not tiene_solicitudes_activas,
                'rrhh': rrhh,
                'Solicitudes': True,
                'CARGOS_CHOICES': ['Presidente','Secretario'],
            })
        
        except Exception as e:
            print(e)
            return Login_views.redirigir_usuario(request=request)




class Rechazar_Solicitud(View):
    def get(self, request):
        return Solicitudes.Notificacion(request=request)
    
    def post(self, request:HttpRequest):
        rrhh = None
        solicitud_id = None
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
        except Exception as e:
            return Login_views.redirigir_usuario(request=request)
        
        try:
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = Aspirante_models.SolicitudCambioCategoria.objects.get(id=solicitud_id,estado="Pendiente")
            solicitud.estado = 'Rechazada'
            if not request.POST.get('observaciones') in [None, '']:
                solicitud.observaciones = request.POST.get('observaciones')
            solicitud.save()
            return Solicitudes.Notificacion(request=request, Success="Solicitud rechazada con éxito")
        except Exception as e:
            return Solicitudes.Notificacion(request=request, Error="Solicitud no encontrada")




def filtrar_solicitudes(request: HttpRequest):
    if not request.method == 'POST':
        return Solicitudes.Notificacion(request=request)

    solicitudes = Aspirante_models.SolicitudCambioCategoria.objects.all().order_by('-fecha_solicitud')
    
    ESTADOS = Aspirante_models.ESTADOS
    CATEGORIAS = Admin_models.CATEGORIA_DOCENTE_CHOICES
    
    filtros = {
        'estado': request.POST.get('estado'),
        'categoria': request.POST.get('categoria'),
        'fecha_inicio': request.POST.get('fecha_inicio'),
        'fecha_fin': request.POST.get('fecha_fin'),
        'busqueda': request.POST.get('busqueda')
    }

    if filtros['estado'] and filtros['estado'] != 'Todos':
        solicitudes = solicitudes.filter(estado=filtros['estado'])
    
    if filtros['categoria'] and filtros['categoria'] != 'Todas':
        solicitudes = solicitudes.filter(categoria_solicitada=filtros['categoria'])
    
    if filtros['fecha_inicio']:
        try:
            fecha_inicio = datetime.strptime(filtros['fecha_inicio'], '%Y-%m-%d').date()
            solicitudes = solicitudes.filter(fecha_solicitud__date__gte=fecha_inicio)
        except (ValueError, TypeError):
            pass
    
    if filtros['fecha_fin']:
        try:
            fecha_fin = datetime.strptime(filtros['fecha_fin'], '%Y-%m-%d').date()
            solicitudes = solicitudes.filter(fecha_solicitud__date__lte=fecha_fin)
        except (ValueError, TypeError):
            pass
    
    if filtros['busqueda']:
        solicitudes = solicitudes.filter(
            Q(aspirante__nombres__icontains=filtros['busqueda']) |
            Q(aspirante__primer_apellido__icontains=filtros['busqueda']) |
            Q(aspirante__segundo_apellido__icontains=filtros['busqueda']) |
            Q(aspirante__ci__icontains=filtros['busqueda']) |
            Q(aspirante__solapin__icontains=filtros['busqueda'])
        )

    solicitudes_por_estado = {
        estado: solicitudes.filter(estado=estado) 
        for estado in ESTADOS
    }
    
    try:
        rrhh = Admin_models.RRHH.objects.get(userid=request.user)
    except:
        rrhh = None
    
    tiene_solicitudes_activas = solicitudes.filter(estado__in=['Pendiente', 'En revisión']).exists()

    context = {
        "Cambio_categoria": True,
        "solicitudes_por_estado": solicitudes_por_estado,
        "estados_filtro": ESTADOS,
        "categorias_filtro": CATEGORIAS,
        "filtros_aplicados": filtros,
        "total_solicitudes": solicitudes.count(),
        "puede_solicitar": not tiene_solicitudes_activas,
        'rrhh': rrhh,
        'Solicitudes': True,
        'CARGOS_CHOICES': ['Presidente','Secretario'],
    }
    return render(request, 'RRHH/solicitudes.html', context)




#################################################################################################################
####################        TRIBUNAL       ######################################################################
#################################################################################################################


class Asignar_tribunal(View):
    def get(self, request):
        return Solicitudes.Notificacion(request=request)

    def post(self, request: HttpRequest):
        if request.method == "POST":
            try:
                rrhh = Admin_models.RRHH.objects.get(userid=request.user)
            except Exception as e:
                print(e)
                return Login_views.redirigir_usuario(request=request)
            
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = None
            try:
                solicitud = Aspirante_models.SolicitudCambioCategoria.objects.get(id=solicitud_id)
            except Exception as e:
                print(e)
                return Solicitudes.Notificacion(request=request, Error="La solicitud no está registrada.")
            
            if solicitud.estado != 'Pendiente':
                return Solicitudes.Notificacion(request=request, Error="La solicitud debe estar en estado Pendiente.")
            
            profesor_ci = str(request.POST.get('profesor_ci')).strip()
            profesor = None
            try:
                profesor = Admin_models.Aspirante.objects.get(ci=profesor_ci, tipo="Profesor")
            except Exception as e:
                print(e)
                return Solicitudes.Notificacion(request=request, Error="El profesor no está registrado.")
            
            # Verificar que el profesor no sea el mismo que hizo la solicitud
            if profesor.userid == solicitud.aspirante.userid:
                return Solicitudes.Notificacion(request=request, Error="No puede asignar al propio solicitante como tribunal.")
            
            cargo = request.POST.get('cargo')
            if cargo not in ['Presidente', 'Secretario']:
                return Solicitudes.Notificacion(request=request, Error="Seleccione un cargo válido.")
            
            # Diccionario de validación de categorías según Resolución 145/2023
            # Clave: categoría solicitada
            # Valor: lista de categorías permitidas para los miembros del tribunal
            CATEGORIAS_TRIBUNAL = {
                'Profesor Titular': ['Profesor Titular'],
                'Profesor Auxiliar': ['Profesor Titular'],
                'Profesor Asistente': ['Profesor Titular', 'Profesor Auxiliar'],
                'Instructor': ['Profesor Titular', 'Profesor Auxiliar'],
                'ATD Superior': ['Profesor Titular', 'Profesor Auxiliar'],
                'ATD Medio Superior': ['Profesor Auxiliar', 'Profesor Asistente']
            }
            
            # Validación de categorías
            categoria_solicitada = solicitud.categoria_solicitada
            categoria_profesor = profesor.categoria_docente
            
            if categoria_solicitada not in CATEGORIAS_TRIBUNAL:
                return Solicitudes.Notificacion(
                    request=request,
                    Error=f"Categoría solicitada {categoria_solicitada} no tiene una configuración de tribunal definida."
                )
            
            if categoria_profesor not in CATEGORIAS_TRIBUNAL[categoria_solicitada]:
                categorias_permitidas = ", ".join(CATEGORIAS_TRIBUNAL[categoria_solicitada])
                return Solicitudes.Notificacion(
                    request=request,
                    Error=f"Para evaluar {categoria_solicitada}, el tribunal debe estar compuesto por Profesores con categorías: {categorias_permitidas}."
                )
            
            tribunal, created = RRHH_models.Tribunal.objects.get_or_create(solicitud_id=solicitud)
            
            # Validar que no exista ya un miembro con el mismo cargo en el tribunal
            if RRHH_models.Miembro_tribunal.objects.filter(tribunal_id=tribunal, cargo=cargo).exists():
                return Solicitudes.Notificacion(
                    request=request, 
                    Error=f"Ya existe un {cargo} asignado a este tribunal. Solo puede haber un {cargo} por tribunal."
                )
            
            # Validar que el profesor no esté ya asignado al tribunal (en cualquier cargo)
            if RRHH_models.Miembro_tribunal.objects.filter(tribunal_id=tribunal, miembro=profesor).exists():
                return Solicitudes.Notificacion(request=request, Error="El profesor ya fue asignado a este tribunal.")
            
            chat = Chat_models.Chat.objects.get(solicitud_id=solicitud)
            Chat_models.Miembro_Chat.objects.create(
                chat_id=chat, userid=profesor.userid,
                tipo="Tribunal"
            )

            miembro = RRHH_models.Miembro_tribunal(tribunal_id=tribunal, miembro=profesor, cargo=cargo)
            miembro.save()
            
            return Solicitudes.Notificacion(request=request, Success=f"El profesor fue asignado como {cargo} con éxito.")
        else:
            return Solicitudes.Notificacion(request=request)


class EliminarMiembroTribunal(View):
    def get(self,request):
        return Solicitudes.Notificacion(request=request)
    
    def post(self, request):
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
        except Exception as e:
            return Login_views.redirigir_usuario(request=request)
        
        try:
            solicitud_id = request.POST.get('solicitud_id')
            member_id = request.POST.get('member_id')
            
            solicitud = Aspirante_models.SolicitudCambioCategoria.objects.get(id=solicitud_id)
            if solicitud.estado != 'Pendiente':
                return Solicitudes.Notificacion(request=request, Error="Solo se pueden modificar tribunales en solicitudes pendientes")
            
            tribunal = RRHH_models.Tribunal.objects.get(solicitud_id=solicitud)
            miembro = RRHH_models.Miembro_tribunal.objects.get(id=member_id, tribunal_id=tribunal)
            chat = Chat_models.Chat.objects.get(solicitud_id=solicitud)
            miembro_chat = Chat_models.Miembro_Chat.objects.get(chat_id=chat,userid=miembro.miembro.userid)
            miembro_chat.delete()
            miembro.delete()
            
            # Check if there are any members left in the tribunal using the related_name
            if not tribunal.miembros.exists():  # Using the related_name 'miembros'
                tribunal.delete()
            
            return Solicitudes.Notificacion(request=request, Success="El profesor ha sido eliminado del tribunal correctamente.")
            
        except Aspirante_models.SolicitudCambioCategoria.DoesNotExist:
            return Solicitudes.Notificacion(request=request, Error="Solicitud no encontrada")
        except RRHH_models.Tribunal.DoesNotExist:
            return Solicitudes.Notificacion(request=request, Error="Tribunal no encontrado")
        except RRHH_models.Miembro_tribunal.DoesNotExist:
            return Solicitudes.Notificacion(request=request, Error="Miembro no encontrado")
        except Exception as e:
            return Solicitudes.Notificacion(request=request, Error=str(e))    






class Pasar_a_revision(View):
    def get(self, request):
        return Solicitudes.Notificacion(request=request)
    
    def post(self,request):
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
        except Exception as e:
            return Login_views.redirigir_usuario(request=request)
        
        try:
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = Aspirante_models.SolicitudCambioCategoria.objects.get(id=solicitud_id)
            if solicitud.estado != 'Pendiente':
                return Solicitudes.Notificacion(request=request,Error="Solo se pueden pasar a revision solicitudes pendientes")
            
            solicitud.estado = 'En revisión'
            solicitud.save()
            
            return Solicitudes.Notificacion(request=request,Success="La solicitud ha sido pasada a revision correctamente.")
        except Exception as e:
            return Solicitudes.Notificacion(request=request,Error=str(e))
