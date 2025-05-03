from django.shortcuts import render, redirect
from Administrador import models as Admin_models
from Login import views as Login_views
from django.views import View
from . import models as Aspirante_models

class AspiranteDashboardView(View):
    def get(self, request):
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            
            # Organizar los datos en secciones lógicas
            datos_personales = {
                'Nombres': aspirante.nombres,
                'Apellidos': f"{aspirante.primer_apellido} {aspirante.segundo_apellido or ''}",
                'CI': aspirante.ci,
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
                'Centro de trabajo/estudio': aspirante.centro,
                'Facultad': aspirante.facultad,
                'CES': aspirante.ces,
                'Departamento': aspirante.departamento,
            }

            datos_laborales = {
                'Cargo': aspirante.cargo,
                'Salario': f"{aspirante.salario:.2f}",
                'Categoría docente': aspirante.categoria_docente if aspirante.categoria_docente else 'No aplica',
                'Fecha otorgamiento categoría': aspirante.fecha_otorgamiento_categoria.strftime('%d/%m/%Y') if aspirante.fecha_otorgamiento_categoria else 'No aplica',
                'Grado científico': aspirante.grado_cientifico if aspirante.grado_cientifico else 'No aplica',
                'Fecha otorgamiento grado': aspirante.fecha_otorgamiento_grado.strftime('%d/%m/%Y') if aspirante.fecha_otorgamiento_grado else 'No aplica',
                'Solapín': aspirante.solapin,
            }

            context = {
                'aspirante': aspirante,
                'datos_personales': datos_personales,
                'datos_academicos': datos_academicos,
                'datos_laborales': datos_laborales,
                'full_name': f"{aspirante.nombres} {aspirante.primer_apellido} {aspirante.segundo_apellido or ''}",
            }
            return render(request, 'Aspirante/dashboard_aspirante.html', context)
            
        except Exception as e:
            return Login_views.redirigir_usuario(request)
        






from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import Http404, FileResponse
from collections import defaultdict
import os

class ExpedienteDocenteView(View):
    template_name = 'Aspirante/expediente.html'
    
    TIPOS_DOCUMENTOS = [
        'Certificación académica',
        'Evaluaciones de desempeño',
        'Aval institucional',
        'Publicaciones científicas',
        'Certificado de idiomas',
        'Examen Problemas Sociales Ciencia/Tecnología'
    ]

    def get_context_data(self,aspirante_id:Admin_models.Aspirante):
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

    def get(self, request, *args, **kwargs):
        aspirante = None
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
        except Exception:
            return Login_views.redirigir_usuario(request=request)
        
        context = self.get_context_data(aspirante_id=aspirante)
        return render(request, self.template_name, context)



    def post(self, request, *args, **kwargs):
        try:
            aspirante = self.get_aspirante()
            tipo = request.POST.get('tipo')
            archivo = request.FILES.get('archivo')
            descripcion = request.POST.get('descripcion', '')

            if not tipo or not archivo:
                messages.error(request, 'Tipo y archivo son campos obligatorios')
                return redirect('expediente_docente')

            if tipo not in dict(self.TIPOS_DOCUMENTOS):
                messages.error(request, 'Tipo de documento no válido')
                return redirect('expediente_docente')

            Aspirante_models.DocumentosExpedienteDocente.objects.create(
                aspirante_id=aspirante,
                tipo=tipo,
                archivo=archivo,
                descripcion=descripcion
            )

            messages.success(request, 'Documento subido correctamente')
            return redirect('expediente_docente')

        except Exception as e:
            messages.error(request, f'Error al procesar el documento: {str(e)}')
            return redirect('expediente_docente')