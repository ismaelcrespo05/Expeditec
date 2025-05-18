from django.shortcuts import render, redirect
from Administrador import models as Admin_models
from Login import views as Login_views
from django.views import View
from . import models as Aspirante_models
from django.http import HttpRequest
from Chat import models as Chat_models
class AspiranteDashboardView(View):
    @staticmethod
    def get_contexto(aspirante):
        # Organizar los datos en secciones lógicas
        datos_personales = {
            'Nombres': aspirante.nombres,
            'Apellidos': f"{aspirante.primer_apellido} {aspirante.segundo_apellido or ''}",
            'CI': aspirante.ci,
            'Solapín': aspirante.solapin,
            'Sexo': aspirante.sexo,
            'Lugar de nacimiento': aspirante.lugar_nacimiento,
            'Color de piel': aspirante.color_piel,
            'Estado civil': aspirante.estado_civil,
            'Ciudadano': aspirante.ciudadano,
            'Procedencia social': aspirante.procedencia_social,
            'Dirección particular': aspirante.direccion,
            'Teléfono': aspirante.telefono,
        }

        datos_academicos = {
            'Tipo': aspirante.tipo,
            'Especialidad': aspirante.especialidad,
            'País': aspirante.pais,
            'Facultad': aspirante.facultad,
            'CES': aspirante.ces,
            'Departamento': aspirante.departamento,
        }

        datos_laborales = {
            'Centro de trabajo': aspirante.centro,
            'Cargo': aspirante.cargo,
            'Area':aspirante.area,
            'Salario': f"{aspirante.salario:.2f}",
            'Categoría docente': aspirante.categoria_docente if aspirante.categoria_docente else 'No aplica',
            'Fecha otorgamiento categoría': aspirante.fecha_otorgamiento_categoria.strftime('%d/%m/%Y') if aspirante.fecha_otorgamiento_categoria else 'No aplica',
            'Grado científico': aspirante.grado_cientifico if aspirante.grado_cientifico else 'No aplica',
            'Fecha otorgamiento grado': aspirante.fecha_otorgamiento_grado.strftime('%d/%m/%Y') if aspirante.fecha_otorgamiento_grado else 'No aplica',
        }

        
        return {
            'Dashboard':True,
            'aspirante': aspirante,
            'datos_personales': datos_personales,
            'datos_academicos': datos_academicos,
            'datos_laborales': datos_laborales,
            'full_name': f"{aspirante.nombres} {aspirante.primer_apellido} {aspirante.segundo_apellido or ''}",
            'tribunales':is_tribunal(aspirante),
        }
    
    @staticmethod
    def Notificacion(request:HttpRequest,Error=None,Success=None):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            context = AspiranteDashboardView.get_contexto(aspirante)
            context['Error'] = Error
            context['Success'] = Success
            return render(request, 'Aspirante/dashboard_aspirante.html', context)
        except Exception as e:
            return Login_views.redirigir_usuario(request)
        
    def get(self, request):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            context = AspiranteDashboardView.get_contexto(aspirante)
            return render(request, 'Aspirante/dashboard_aspirante.html', context)
            
        except Exception as e:
            return Login_views.redirigir_usuario(request)
        

########################################################################################################
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import Http404, FileResponse
from django.views import View
from collections import defaultdict
import os

class ExpedienteDocenteView(View):
    template_name = 'Aspirante/expediente.html'
    
    TIPOS_DOCUMENTOS = Aspirante_models.TIPOS_DOCUMENTOS

    def get_context_data(self, aspirante_id):
        documentos = Aspirante_models.DocumentosExpedienteDocente.objects.filter(
            aspirante_id=aspirante_id
        ).order_by('-fecha_subida')
        
        # Organizar documentos por tipo
        documentos_por_tipo = defaultdict(list)
        for doc in documentos:
            documentos_por_tipo[doc.tipo].append(doc)
        
        # Ordenar según el orden definido en TIPOS_DOCUMENTOS
        documentos_ordenados = {}
        for tipo in self.TIPOS_DOCUMENTOS:
            if tipo in documentos_por_tipo:
                documentos_ordenados[tipo] = documentos_por_tipo[tipo]
        
        return {
            'TIPOS_DOCUMENTOS': self.TIPOS_DOCUMENTOS,
            'documentos_por_tipo': documentos_ordenados,
            'aspirante': aspirante_id,
            'tribunales':is_tribunal(aspirante_id),
        }
    


    @staticmethod
    def Notificacion(request, template_name, aspirante_id, Error=None, Success=None):
        try:
            context = ExpedienteDocenteView.get_context_data(ExpedienteDocenteView(), aspirante_id=aspirante_id)
            context['Error'] = Error
            context['Success'] = Success
            return render(request, template_name, context)
        except Exception:
            return Login_views.redirigir_usuario(request=request)




    def get(self, request, *args, **kwargs):
        aspirante = None
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
        except Exception:
            return Login_views.redirigir_usuario(request=request)
        
        context = self.get_context_data(aspirante_id=aspirante)
        context['Expediente'] = True
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            tipo = request.POST.get('tipo')
            archivo = request.FILES.get('archivo')
            descripcion = request.POST.get('descripcion', '')

            if not tipo or not archivo:
                return self.Notificacion(
                    request=request,
                    template_name=self.template_name,
                    aspirante_id=aspirante,
                    Error='Tipo y archivo son campos obligatorios'
                )

            if tipo not in self.TIPOS_DOCUMENTOS:
                return self.Notificacion(
                    request=request,
                    template_name=self.template_name,
                    aspirante_id=aspirante,
                    Error='Tipo de documento no válido'
                )

            Aspirante_models.DocumentosExpedienteDocente.objects.create(
                aspirante_id=aspirante,
                tipo=tipo,
                archivo=archivo,
                descripcion=descripcion
            )

            return self.Notificacion(
                request=request,
                template_name=self.template_name,
                aspirante_id=aspirante,
                Success='Documento subido correctamente'
            )            

        except Exception as e:
            return self.Notificacion(
                request=request,
                template_name=self.template_name,
                aspirante_id=aspirante,
                Error=str(e)
            )
        




class Eliminar_ExpedienteDocenteView(View):
    template_name = 'Aspirante/expediente.html'
    def get(self,request:HttpRequest):
        aspirante_id = None
        try:
            aspirante_id = Admin_models.Aspirante.objects.get(userid=request.user)
        except Exception as e:
            return Login_views.redirigir_usuario(request)
        
        return ExpedienteDocenteView.Notificacion(request,template_name=self.template_name,aspirante_id=aspirante_id)

    def post(self,request):
        aspirante_id = None
        try:
            aspirante_id = Admin_models.Aspirante.objects.get(userid=request.user)
        except Exception as e:
            return Login_views.redirigir_usuario(request)
        
        if request.POST:
            documento_id = request.POST.get('documento_id')
            try:
                documento = Aspirante_models.DocumentosExpedienteDocente.objects.get(id=documento_id)
                documento.delete()
                return ExpedienteDocenteView.Notificacion(request,template_name=self.template_name,aspirante_id=aspirante_id,Success="Documento eliminado correctamente")
            except Exception as e:
                return ExpedienteDocenteView.Notificacion(request,template_name=self.template_name,aspirante_id=aspirante_id,Error="Documento no encontrado")
        return ExpedienteDocenteView.Notificacion(request,template_name=self.template_name,aspirante_id=aspirante_id)





class Update_ExpedienteDocenteView(View):
    template_name = 'Aspirante/expediente.html'
    def get(self,request:HttpRequest):
        aspirante_id = None
        try:
            aspirante_id = Admin_models.Aspirante.objects.get(userid=request.user)
        except Exception as e:
            return Login_views.redirigir_usuario(request)
        
        return ExpedienteDocenteView.Notificacion(request,template_name=self.template_name,aspirante_id=aspirante_id)

    def post(self,request):
        aspirante_id = None
        try:
            aspirante_id = Admin_models.Aspirante.objects.get(userid=request.user)
        except Exception as e:
            return Login_views.redirigir_usuario(request)
        
        if request.POST:
            documento_id = request.POST.get('documento_id')
            archivo = request.FILES.get('archivo')
            
            if not archivo:
                return ExpedienteDocenteView.Notificacion(
                    request=request,
                    template_name=self.template_name,
                    aspirante_id=aspirante_id,
                    Error='Tipo y archivo son campos obligatorios'
                )
            
            try:
                documento = Aspirante_models.DocumentosExpedienteDocente.objects.get(id=documento_id)
                documento.archivo.delete()
                documento.archivo=archivo
                documento.save()
                return ExpedienteDocenteView.Notificacion(request,template_name=self.template_name,aspirante_id=aspirante_id,Success="Documento actualizado correctamente")
            except Exception as e:
                return ExpedienteDocenteView.Notificacion(request,template_name=self.template_name,aspirante_id=aspirante_id,Error="Documento no encontrado")
        return ExpedienteDocenteView.Notificacion(request,template_name=self.template_name,aspirante_id=aspirante_id)

##########################################################################################################################
##########################################################################################################################
##########################################################################################################################


class Cambio_Categoria(View):
    @staticmethod
    def Notificacion(request,Error=None,Success=None):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            
            # Obtenemos todas las solicitudes ordenadas por fecha descendente
            solicitudes = Aspirante_models.SolicitudCambioCategoria.objects.filter(
                aspirante=aspirante
            ).order_by('-fecha_solicitud')
            
            # Definimos los estados posibles
            ESTADOS = ['Pendiente', 'En revisión', 'Aprobada', 'Rechazada']
            
            # Pre-filtramos las solicitudes por estado
            solicitudes_por_estado = {
                estado: solicitudes.filter(estado=estado) 
                for estado in ESTADOS
            }
            
            # Calculamos el total de solicitudes
            total_solicitudes = solicitudes.count()
            
            # Verificamos si puede solicitar (no tiene solicitudes pendientes o en revisión)
            puede_solicitar = not solicitudes.filter(
                estado__in=['Pendiente', 'En revisión']
            ).exists()
            if aspirante.categoria_docente == 'Titular':
                puede_solicitar = False
            

            # Definimos el orden de las categorías
            orden_categorias = Admin_models.CATEGORIA_DOCENTE_CHOICES

            # Obtenemos el índice de la categoría actual del aspirante
            try:
                indice_actual = orden_categorias.index(aspirante.categoria_docente)
            except ValueError:
                indice_actual = -1

            # Calculamos la categoría siguiente si existe
            categorias_disponibles = []
            if indice_actual >= 0 and indice_actual + 1 < len(orden_categorias):
                siguiente_categoria = orden_categorias[indice_actual + 1]
                if siguiente_categoria != 'Titular' or aspirante.categoria_docente != 'Titular':
                    categorias_disponibles = [siguiente_categoria]
            
            print(categorias_disponibles)
            return render(request, 'Aspirante/cambio_categoria.html', {
                "Cambio_categoria": True,
                "solicitudes_por_estado": solicitudes_por_estado,
                "ESTADOS": ESTADOS,
                "puede_solicitar": puede_solicitar,
                "CATEGORIA_DOCENTE_CHOICES": categorias_disponibles,
                "categoria_actual": aspirante.categoria_docente,
                "total_solicitudes": total_solicitudes,  # Nuevo campo añadido
                'tribunales':is_tribunal(aspirante),
                'Error':Error,'Success':Success
            })
            
        except Admin_models.Aspirante.DoesNotExist:
            return Login_views.redirigir_usuario(request)
        
    def get(self, request):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            
            # Obtenemos todas las solicitudes ordenadas por fecha descendente
            solicitudes = Aspirante_models.SolicitudCambioCategoria.objects.filter(
                aspirante=aspirante
            ).order_by('-fecha_solicitud')
            
            # Definimos los estados posibles
            ESTADOS = ['Pendiente', 'En revisión', 'Aprobada', 'Rechazada']
            
            # Pre-filtramos las solicitudes por estado
            solicitudes_por_estado = {
                estado: solicitudes.filter(estado=estado) 
                for estado in ESTADOS
            }
            
            # Calculamos el total de solicitudes
            total_solicitudes = solicitudes.count()
            
            # Verificamos si puede solicitar (no tiene solicitudes pendientes o en revisión)
            puede_solicitar = not solicitudes.filter(
                estado__in=['Pendiente', 'En revisión']
            ).exists()
            if aspirante.categoria_docente == 'Titular':
                puede_solicitar = False
            

            # Definimos el orden de las categorías
            orden_categorias = Admin_models.CATEGORIA_DOCENTE_CHOICES

            # Obtenemos el índice de la categoría actual del aspirante
            try:
                indice_actual = orden_categorias.index(aspirante.categoria_docente)
            except ValueError:
                indice_actual = -1

            # Calculamos la categoría siguiente si existe
            categorias_disponibles = []
            if indice_actual >= 0 and indice_actual + 1 < len(orden_categorias):
                siguiente_categoria = orden_categorias[indice_actual + 1]
                if siguiente_categoria != 'Titular' or aspirante.categoria_docente != 'Titular':
                    categorias_disponibles = [siguiente_categoria]
            
            print(categorias_disponibles)
            return render(request, 'Aspirante/cambio_categoria.html', {
                "Cambio_categoria": True,
                "solicitudes_por_estado": solicitudes_por_estado,
                "ESTADOS": ESTADOS,
                "puede_solicitar": puede_solicitar,
                "CATEGORIA_DOCENTE_CHOICES": categorias_disponibles,
                "categoria_actual": aspirante.categoria_docente,
                "total_solicitudes": total_solicitudes,  # Nuevo campo añadido
                'tribunales':is_tribunal(aspirante),
            })
            
        except Admin_models.Aspirante.DoesNotExist:
            return Login_views.redirigir_usuario(request)
        

    def post(self, request):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            return Cambio_Categoria.Notificacion(request)
        except Exception as e:
            return Login_views.redirigir_usuario(request)


class Generar_Solicitud(View):
    def get(self,request:HttpRequest):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            return Cambio_Categoria.Notificacion(request)
        except Exception as e:
            return Login_views.redirigir_usuario(request)
    

    def post(self, request:HttpRequest):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            categoria_solicitada = request.POST.get('categoria_solicitada')
            
            # Verificar que la categoría solicitada sea válida
            if not categoria_solicitada in Admin_models.CATEGORIA_DOCENTE_CHOICES:
                return Cambio_Categoria.Notificacion(request=request, Error="Categoría docente inválida")
            
            # Definir el orden de las categorías
            orden_categorias = Admin_models.CATEGORIA_DOCENTE_CHOICES
            
            # Verificar si el aspirante ya es titular
            if aspirante.categoria_docente == 'Titular':
                return Cambio_Categoria.Notificacion(
                    request=request, 
                    Error="No puede solicitar cambio de categoría porque ya tiene la máxima categoría docente (Titular)"
                )
            
            # Obtener índices de las categorías actual y solicitada
            try:
                indice_actual = orden_categorias.index(aspirante.categoria_docente)
                indice_solicitada = orden_categorias.index(categoria_solicitada)
            except ValueError:
                return Cambio_Categoria.Notificacion(request=request, Error="Categoría actual o solicitada no válida")
            
            # Validar que la categoría solicitada sea exactamente un nivel superior
            if indice_solicitada != indice_actual + 1:
                return Cambio_Categoria.Notificacion(
                    request=request, 
                    Error=f"Solo puede solicitar una categoría inmediatamente superior. Su categoría actual es {aspirante.categoria_docente}, puede solicitar {orden_categorias[indice_actual + 1]}"
                )
            
            # Verificar si ya existe una solicitud pendiente o en revisión
            if Aspirante_models.SolicitudCambioCategoria.objects.filter(aspirante=aspirante, estado__in=['Pendiente','En revisión']).exists():
                return Cambio_Categoria.Notificacion(request=request, Error="Ya hay una solicitud pendiente o en revisión")
            
            # Crear la solicitud si pasa todas las validaciones
            solicitud = Aspirante_models.SolicitudCambioCategoria.objects.create(
                aspirante=aspirante,
                categoria_solicitada=categoria_solicitada
            )
            
            # Crear el chat asociado
            chat = Chat_models.Chat.objects.create(
                solicitud_id=solicitud
            )
            
            # Agregar al aspirante al chat
            Chat_models.Miembro_Chat.objects.create(
                chat_id=chat, userid=request.user,
                tipo=aspirante.tipo
            )
            
            # Agregar a todos los RRHH al chat
            rrhh = Admin_models.RRHH.objects.all()
            for rh in rrhh:
                Chat_models.Miembro_Chat.objects.create(
                    chat_id=chat, userid=rh.userid,
                    tipo="RRHH"
                )
                
            return Cambio_Categoria.Notificacion(request=request, Success="Solicitud enviada con éxito")
            
        except Exception as e:
            print(e)
            return Login_views.redirigir_usuario(request)    

def Eliminar_Solicitud(request:HttpRequest):
    aspirante = None
    try:
        aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
    except Exception as e:
        print(e)
        return Login_views.redirigir_usuario(request)
    if request.POST:
        solicitud_id = request.POST.get('solicitud_id')
        try:
            solicitud = Aspirante_models.SolicitudCambioCategoria.objects.get(id=solicitud_id,aspirante=aspirante)
            if solicitud.estado in ['Pendiente','En revisión']:
                solicitud.delete()
                return Cambio_Categoria.Notificacion(request=request,Success="Solicitud cancelada con éxito")
            return Cambio_Categoria.Notificacion(request=request,Success="La solicitud ya fue finalizada")
        except Exception as e:
            print(e)
            return Cambio_Categoria.Notificacion(request=request,Error="Solicitud no encontrada")
    else:
        return Cambio_Categoria.Notificacion(request=request)
    

from RRHH import models as RRHH_models
def is_tribunal(aspirante:Admin_models.Aspirante = None,request:HttpRequest = None):
    if aspirante:
        membresia = RRHH_models.Miembro_tribunal.objects.filter(miembro=aspirante).values_list('tribunal_id')
        membresia = RRHH_models.Tribunal.objects.filter(id__in=membresia).values_list('solicitud_id')
        membresia = Aspirante_models.SolicitudCambioCategoria.objects.filter(id__in=membresia,estado='En revisión')
        return False if not membresia else True
    else:
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            membresia = RRHH_models.Miembro_tribunal.objects.filter(miembro=aspirante).values_list('tribunal_id')
            membresia = RRHH_models.Tribunal.objects.filter(id__in=membresia).values_list('solicitud_id')
            membresia = Aspirante_models.SolicitudCambioCategoria.objects.filter(id__in=membresia,estado='En revisión')
            return False if not membresia else True
        except Exception as e:
            return False
    
    


class Tribunal(View):
    @staticmethod
    def Notificacion(request,Error=None, Success=None):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            if is_tribunal(aspirante):            
                # Obtenemos todas las solicitudes ordenadas por fecha descendente (más recientes primero)
                tribunales = RRHH_models.Miembro_tribunal.objects.filter(miembro=aspirante).values_list('tribunal_id').distinct()
                tribunales = RRHH_models.Tribunal.objects.filter(id__in=tribunales).values_list('solicitud_id')
                solicitudes = Aspirante_models.SolicitudCambioCategoria.objects.filter(id__in=tribunales,estado='En revisión').order_by('-fecha_solicitud')
                # Definimos los estados posibles
                ESTADOS = ['Pendiente', 'En revisión', 'Aprobada', 'Rechazada']
                
                # Pre-filtramos las solicitudes por estado
                solicitudes_por_estado = {
                    estado: solicitudes.filter(estado=estado) 
                    for estado in ESTADOS
                }
                return render(request,'Tribunal/tribunal.html', {
                    "Tribunales": True,
                    "solicitudes_por_estado": solicitudes_por_estado,
                    "ESTADOS": ESTADOS,
                    "categoria_actual": aspirante.categoria_docente,
                    'tribunales':is_tribunal(aspirante),
                    'Error':Error,'Success':Success
                })
            else:
                return AspiranteDashboardView.Notificacion(request=request,Error="No eres miembro de ningún tribunal.")    
        except Exception as e:
            print(e)
        return Login_views.redirigir_usuario(request)

    def get(self,request):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            if is_tribunal(aspirante):            
                # Obtenemos todas las solicitudes ordenadas por fecha descendente (más recientes primero)
                tribunales = RRHH_models.Miembro_tribunal.objects.filter(miembro=aspirante).values_list('tribunal_id').distinct()
                tribunales = RRHH_models.Tribunal.objects.filter(id__in=tribunales).values_list('solicitud_id')
                solicitudes = Aspirante_models.SolicitudCambioCategoria.objects.filter(id__in=tribunales,estado='En revisión').order_by('-fecha_solicitud')
                # Definimos los estados posibles
                ESTADOS = ['Pendiente', 'En revisión', 'Aprobada', 'Rechazada']
                
                # Pre-filtramos las solicitudes por estado
                solicitudes_por_estado = {
                    estado: solicitudes.filter(estado=estado) 
                    for estado in ESTADOS
                }
                return render(request,'Tribunal/tribunal.html', {
                    "Tribunales": True,
                    "solicitudes_por_estado": solicitudes_por_estado,
                    "ESTADOS": ESTADOS,
                    "categoria_actual": aspirante.categoria_docente,
                    'tribunales':is_tribunal(aspirante),
                })
            else:
                return AspiranteDashboardView.Notificacion(request=request,Error="No eres miembro de ningún tribunal.")    
        except Exception as e:
            print(e)
        return Login_views.redirigir_usuario(request)

    def post(self, request):
        aspirante = None
        solicitud = None
        tribunal = None
        miembro = None
        #validar aspirante
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
        except Exception as e:
            print(e)
            return Login_views.redirigir_usuario(request=request)
        
        #validar solicitud y que es miembro de tribunal
        if is_tribunal(aspirante):
            solicitud_id = request.POST.get('solicitud_id')
            try:
                solicitud = Aspirante_models.SolicitudCambioCategoria.objects.get(id=solicitud_id)
                tribunal = RRHH_models.Tribunal.objects.get(solicitud_id=solicitud)
            except Exception as e:
                print(e)
                return AspiranteDashboardView.Notificacion(request=request,Error="Error al procesar la solicitud.")    
        else:
            return AspiranteDashboardView.Notificacion(request=request,Error="No eres miembro de ningún tribunal.")    
        
        #validar si es miembro
        try:
            miembro = RRHH_models.Miembro_tribunal.objects.get(tribunal_id=tribunal,miembro=aspirante)
        except Exception as e:
            print(e)
            return Tribunal.Notificacion(request=request,Error="Usted no es miembro de este tribunal.")
        
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Tribunal.Notificacion(request=request,Error="El campo de archivo es obligatorio.")
        
        descripcion = request.POST.get('descripcion')

        acta = Aspirante_models.Actas_Tribunal.objects.create(
            solicitud_id=solicitud,
            archivo = archivo,
            descripcion=descripcion,
            miembro=miembro
        )
        acta.save()
        return Tribunal.Notificacion(request=request,Success="El acta se ha publicado con éxito.")

        
    


class Aprobar_solicitud(View):
    def get(self,request):
        pass

    def post(self,request):
        pass



class Rechazar_solicitud(View):
    def get(self, request):
        return Tribunal.Notificacion(request=request)
    
    def post(self, request:HttpRequest):
        aspirante = None
        tribunal=None
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            tribunal = is_tribunal(aspirante=aspirante)
        except Exception as e:
            print(e)
            pass
        
        if not tribunal:
            return Login_views.redirigir_usuario(request=request)
        
        solicitud_id = None
        try:
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = Aspirante_models.SolicitudCambioCategoria.objects.get(id=solicitud_id)
        except Exception as e:
            print(e)
            return Tribunal.Notificacion(request=request, Error="Solicitud no encontrada")
        try:
            tribunal = RRHH_models.Tribunal.objects.get(solicitud_id=solicitud)
            presidente = RRHH_models.Miembro_tribunal.objects.get(tribunal_id=tribunal,miembro=aspirante,cargo="Presidente")
            solicitud.estado = 'Rechazada'
            if not request.POST.get('observaciones') in [None, '']:
                solicitud.observaciones = request.POST.get('observaciones')
            solicitud.save()
            return AspiranteDashboardView.Notificacion(request=request, Success="Solicitud rechazada correctamente")
        except Exception as e:
            print(e)
            return Tribunal.Notificacion(request=request, Error="Acceso denegado.")



class Aprobar_solicitud(View):
    def get(self, request):
        return Tribunal.Notificacion(request=request)
    
    def post(self, request:HttpRequest):
        aspirante = None
        tribunal=None
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            tribunal = is_tribunal(aspirante=aspirante)
        except Exception as e:
            print(e)
            pass
        
        if not tribunal:
            return Login_views.redirigir_usuario(request=request)
        
        solicitud_id = None
        try:
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = Aspirante_models.SolicitudCambioCategoria.objects.get(id=solicitud_id)
        except Exception as e:
            print(e)
            return Tribunal.Notificacion(request=request, Error="Solicitud no encontrada")
        try:
            tribunal = RRHH_models.Tribunal.objects.get(solicitud_id=solicitud)
            presidente = RRHH_models.Miembro_tribunal.objects.get(tribunal_id=tribunal,miembro=aspirante,cargo="Presidente")
            solicitud.estado = 'Aprobada'
            if not request.POST.get('observaciones') in [None, '']:
                solicitud.observaciones = request.POST.get('observaciones')

            solicitud.aspirante.categoria_docente = solicitud.categoria_solicitada
            solicitud.aspirante.save()
            solicitud.save()
            return AspiranteDashboardView.Notificacion(request=request, Success="Solicitud aprobada correctamente")
        except Exception as e:
            print(e)
            return Tribunal.Notificacion(request=request, Error="Acceso denegado.")




class Eliminar_acta_tribunal(View):
    def get(self,request:HttpRequest):
        return Tribunal.Notificacion(request=request)

    def post(self, request:HttpRequest):
        aspirante = None
        tribunal=None
        miembro = None
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            tribunal = is_tribunal(aspirante=aspirante)

        except Exception as e:
            print(e)
            pass
        
        if not tribunal:
            return Login_views.redirigir_usuario(request=request)
        



        acta = None
        try:
            acta_id = request.POST.get('acta_id')
            acta = Aspirante_models.Actas_Tribunal.objects.get(id=acta_id)
        except Exception as e:
            return Tribunal.Notificacion(request=request, Error="Acta no encontrada")
        
        try:
            tribunal = RRHH_models.Tribunal.objects.get(solicitud_id=acta.solicitud_id)
        except Exception as e:
            print(e)
            return Tribunal.Notificacion(request=request,Error="Tribunal no registrado.")

        try:
            miembro = RRHH_models.Miembro_tribunal.objects.get(miembro=aspirante,tribunal_id=tribunal)
            if miembro.cargo == "Presidente" or acta.miembro.id == miembro.id:
                acta.delete()
                return Tribunal.Notificacion(request=request,Success="Acta eliminada correctamente.")
            else:
                return Tribunal.Notificacion(request=request,Error="Usted no esta autorizado a eliminar esta acta.")
        except Exception as e:
            print(e)
            return Tribunal.Notificacion(request=request,Error="Usted no es miembro de este tribunal.")        

        
