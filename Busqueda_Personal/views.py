from django.shortcuts import render,redirect
from django.http import HttpRequest
from Login import views as Login_views
from Administrador import models as Admin_models
from Aspirante import models as Aspirante_models
from django.utils.html import escape
from django.views import View
from django.db.models import Q
from Configuracion import views as Config_views
from collections import defaultdict
# Create your views here.

class Busqueda_Personal(View):
    def get(self,request:HttpRequest):
        return Login_views.redirigir_usuario(request=request)
    

    def post(self, request:HttpRequest):
        rrhh = None
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
        except Exception as e:
            pass

        if not request.user.is_staff and not rrhh:
            return Login_views.redirigir_usuario(request=request)
        
        else:
            buscar_old = escape(request.POST.get('buscar').strip())
            buscar = buscar_old.lower()
            if buscar:
                # Campos donde se buscará (solo los requeridos)
                campos_busqueda = [
                    'nombres',
                    'primer_apellido',
                    'segundo_apellido',
                    'ci',
                ]
                
                # Construir consulta OR para buscar en todos los campos
                consulta = Q()
                for campo in campos_busqueda:
                    consulta |= Q(**{f"{campo}__icontains": buscar})  # Búsqueda insensible a mayúsculas/minúsculas
                
                # Filtrar aspirantes que cumplan al menos una condición
                aspirantes = Admin_models.Aspirante.objects.filter(consulta).distinct().order_by('nombres', 'primer_apellido')
            
                return render(request, 'Busqueda_Personal/lista_personal.html', {
                    'aspirantes':aspirantes,'termino_busqueda':buscar_old,
                    'total_resultados': aspirantes.count(),
                    'rrhh':rrhh,
                    'base':Config_views.get_base(request=request)
                })
            else:
                # Si no hay término de búsqueda, mostrar todos ordenados
                return render(request, 'Busqueda_Personal/lista_personal.html', {
                    'aspirantes': Admin_models.Aspirante.objects.all().order_by('nombres', 'primer_apellido'),
                    'termino_busqueda': '',
                    'total_resultados': Admin_models.Aspirante.objects.count(),
                    'rrhh':rrhh,
                    'base':Config_views.get_base(request=request),
                })
        
    

from Aspirante import views as Aspirante_views
class Expedientes_Personal(View):
    TIPOS_DOCUMENTOS = Aspirante_models.TIPOS_DOCUMENTOS
    def get(self,request:HttpRequest):
        if request.user.is_staff:
            return Login_views.redirigir_usuario(request=request)
        else:
            try:
                rrhh = Admin_models.RRHH.objects.get(userid=request.user)
                return redirect('solicitudes')
            except Exception as e:
                print(e)
                return Login_views.redirigir_usuario(request=request)
            
            
    
    def post(self,request:HttpRequest):
        rrhh = None

        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
        except Exception as e:
            pass

        aspirante=None
        is_tribunal = None
        Tribunales = False
        try:
            aspirante = Admin_models.Aspirante.objects.get(userid=request.user)
            is_tribunal = Aspirante_views.is_tribunal(aspirante)
            if is_tribunal:
                Tribunales = True
        except Exception as e:
            pass


        if rrhh or request.user.is_staff  or Tribunales:
            aspirante_id = request.POST.get('aspirante_id')

            aspirante = Admin_models.Aspirante.objects.get(id=aspirante_id)
            
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

            ##################################################################################

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
            
            context = {
                'base':Config_views.get_base(request=request),
                'rrhh':rrhh,
                'aspirante': aspirante,
                'tribunales':is_tribunal,
                "Tribunales": True,
                'datos_personales': datos_personales,
                'datos_academicos': datos_academicos,
                'datos_laborales': datos_laborales,
                'full_name': f"{aspirante.nombres} {aspirante.primer_apellido} {aspirante.segundo_apellido or ''}",
                #############################
                'TIPOS_DOCUMENTOS': self.TIPOS_DOCUMENTOS,
                'documentos_por_tipo': documentos_ordenados,
                'aspirante': aspirante_id
            }
            return render(request, 'Expediente/expediente.html', context=context)
        else:
            return Login_views.redirigir_usuario(request=request)
        