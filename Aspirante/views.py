from django.shortcuts import render, redirect
from Administrador import models as Admin_models
from Login import views as Login_views
from django.views import View
from . import models as Aspirante_models
from django.http import HttpRequest
class AspiranteDashboardView(View):
    def get(self, request):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            
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

            context = {
                'Dashboard':True,
                'aspirante': aspirante,
                'datos_personales': datos_personales,
                'datos_academicos': datos_academicos,
                'datos_laborales': datos_laborales,
                'full_name': f"{aspirante.nombres} {aspirante.primer_apellido} {aspirante.segundo_apellido or ''}",
            }
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
            'aspirante': aspirante_id
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



class Cambio_Categoria(View):
    @staticmethod
    def Notificacion(request,Error=None,Success=None):
        aspirante_id = None
        try:
            aspirante_id = Admin_models.Aspirante.objects.get(userid=request.user)
            return render(request,'Aspirante/cambio_categoria.html',{
                "Cambio_categoria":True,
                "Error":Error,'Success':Success
            })
        except Exception as e:
            return Login_views.redirigir_usuario(request)
        
        
    def get(self, request):
        aspirante_id = None
        try:
            aspirante_id = Admin_models.Aspirante.objects.get(userid=request.user)
            return render(request,'Aspirante/cambio_categoria.html',{
                "Cambio_categoria":True
            })
        except Exception as e:
            return Login_views.redirigir_usuario(request)
        

    def post(self, request):
        pass
