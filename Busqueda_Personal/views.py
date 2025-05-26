from django.shortcuts import render,redirect
from django.http import HttpRequest
from Login import views as Login_views
from Administrador import models as Admin_models
from Aspirante import views as Aspirante_views
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
    
    def post(self, request: HttpRequest):
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
                # Campos donde se buscará individualmente
                campos_busqueda = [
                    'nombres',
                    'primer_apellido',
                    'segundo_apellido',
                    'ci',
                    'solapin',
                ]
                
                # Construir consulta OR para buscar en todos los campos
                consulta = Q()
                for campo in campos_busqueda:
                    consulta |= Q(**{f"{campo}__icontains": buscar})
                
                # Búsqueda por nombre completo concatenado
                consulta_nombre_completo = Q()
                
                # Opción 1: Usando annotate (más eficiente si tu DB lo soporta)
                try:
                    from django.db.models import Value as V
                    from django.db.models.functions import Concat
                    
                    aspirantes = Admin_models.Aspirante.objects.annotate(
                        nombre_completo=Concat(
                            'nombres', V(' '), 
                            'primer_apellido', V(' '), 
                            'segundo_apellido'
                        )
                    ).filter(
                        consulta | 
                        Q(nombre_completo__icontains=buscar) |
                        Q(userid__username__icontains=buscar) |
                        Q(userid__email__icontains=buscar)
                    ).distinct().order_by('nombres', 'primer_apellido')
                
                except:
                    # Opción 2: Para bases de datos que no soportan bien Concat
                    aspirantes = Admin_models.Aspirante.objects.filter(consulta).distinct()
                    ids_coincidentes = []
                    for a in aspirantes:
                        nombre_completo = f"{a.nombres} {a.primer_apellido} {a.segundo_apellido or ''}".lower()
                        if buscar in nombre_completo:
                            ids_coincidentes.append(a.id)
                    
                    aspirantes = Admin_models.Aspirante.objects.filter(
                        Q(id__in=ids_coincidentes) |
                        consulta |
                        Q(userid__username__icontains=buscar) |
                        Q(userid__email__icontains=buscar)
                    ).distinct().order_by('nombres', 'primer_apellido')
            
                return render(request, 'Busqueda_Personal/lista_personal.html', {
                    'aspirantes': aspirantes,
                    'termino_busqueda': buscar_old,
                    'total_resultados': aspirantes.count(),
                    'rrhh': rrhh,
                    'base': Config_views.get_base(request=request)
                })
            else:
                # Si no hay término de búsqueda, mostrar todos ordenados
                return render(request, 'Busqueda_Personal/lista_personal.html', {
                    'aspirantes': Admin_models.Aspirante.objects.all().order_by('nombres', 'primer_apellido'),
                    'termino_busqueda': '',
                    'total_resultados': Admin_models.Aspirante.objects.count(),
                    'rrhh': rrhh,
                    'base': Config_views.get_base(request=request),
                })
    

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
        




class Aplicar_filtros(View):
    def get(self, request:HttpRequest):
        if request.user.is_staff or request.user.tipo_usuario == "RRHH":
            rrhh = None
            try:
                rrhh = Admin_models.RRHH.objects.get(userid=request.user)
            except Exception as e:
                pass

            facultades = Admin_models.Aspirante.objects.values_list('facultad', flat=True).distinct()
    
            context = {
                'TIPO_CHOICES': Admin_models.TIPO_CHOICES,
                'SEXO_CHOICES': Admin_models.SEXO_CHOICES,
                'COLOR_PIEL_CHOICES': Admin_models.COLOR_PIEL_CHOICES,
                'ESTADO_CIVIL_CHOICES': Admin_models.ESTADO_CIVIL_CHOICES,
                'PROCEDENCIA_SOCIAL_CHOICES': Admin_models.PROCEDENCIA_SOCIAL_CHOICES,
                'CATEGORIA_DOCENTE_CHOICES': Admin_models.CATEGORIA_DOCENTE_CHOICES,
                'GRADO_CIENTIFICO_CHOICES': Admin_models.GRADO_CIENTIFICO_CHOICES,
                'facultades': facultades,
                'rrhh': rrhh,
                'base': Config_views.get_base(request=request)
            }
            return render(request,'Busqueda_Personal/filtros.html',context)
        else:
            return Login_views.redirigir_usuario(request=request)

    def post(self, request:HttpRequest):
        rrhh = None
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
        except Exception as e:
            pass

        if not request.user.is_staff and not rrhh:
            return Login_views.redirigir_usuario(request=request)
        
        # Obtener todos los parámetros GET del formulario de filtros
        filtros = request.POST
        
        # Iniciar con todos los aspirantes
        queryset = Admin_models.Aspirante.objects.all()
        
        # Mapeo exacto de campos del formulario a campos del modelo
        campos_filtros = {
            # Información Básica
            'nombres': 'nombres__icontains',
            'primer_apellido': 'primer_apellido__icontains',
            'segundo_apellido': 'segundo_apellido__icontains',
            'ci': 'ci__icontains',
            'tipo': 'tipo__exact',
            
            # Datos Personales
            'sexo': 'sexo__exact',
            'lugar_nacimiento': 'lugar_nacimiento__icontains',
            'color_piel': 'color_piel__exact',
            'estado_civil': 'estado_civil__exact',
            'ciudadano': 'ciudadano__icontains',
            
            # Datos Laborales
            'centro': 'centro__icontains',
            'cargo': 'cargo__icontains',
            'facultad': 'facultad__icontains',
            'departamento': 'departamento__icontains',
            'salario_min': 'salario__gte',
            'salario_max': 'salario__lte',
            
            # Información Académica
            'categoria_docente': 'categoria_docente__exact',
            'grado_cientifico': 'grado_cientifico__exact',
            'especialidad': 'especialidad__icontains',
            'solapin': 'solapin__icontains',
            
            # Otros Datos
            'procedencia_social': 'procedencia_social__exact',
            'pais': 'pais__icontains',
            'telefono': 'telefono__icontains',
            'direccion': 'direccion__icontains'
        }
        
        # Construir consulta dinámica
        consulta = Q()
        
        for campo_form, campo_modelo in campos_filtros.items():
            valor = filtros.get(campo_form)
            if valor:
                # Manejar campos de rango numérico
                if campo_form in ['salario_min', 'salario_max']:
                    try:
                        consulta &= Q(**{campo_modelo: float(valor)})
                    except (ValueError, TypeError):
                        continue
                else:
                    consulta &= Q(**{campo_modelo: valor})
        
        # Aplicar la consulta combinada
        if consulta:
            queryset = queryset.filter(consulta).distinct()
        
        # Ordenar resultados
        queryset = queryset.order_by('nombres', 'primer_apellido')
        
    
        
        # Preparar el contexto de respuesta
        contexto = {
            'aspirantes': queryset,
            'termino_busqueda': " | ".join([f"{k}: {v}" for k, v in filtros.items() if v and k != "csrfmiddlewaretoken"]),
            'total_resultados': queryset.count(),
            'rrhh': rrhh,
            'base': Config_views.get_base(request=request),
            # Opciones para los selects
            'TIPO_CHOICES': Admin_models.TIPO_CHOICES,
            'SEXO_CHOICES': Admin_models.SEXO_CHOICES,
            'COLOR_PIEL_CHOICES': Admin_models.COLOR_PIEL_CHOICES,
            'ESTADO_CIVIL_CHOICES': Admin_models.ESTADO_CIVIL_CHOICES,
            'PROCEDENCIA_SOCIAL_CHOICES': Admin_models.PROCEDENCIA_SOCIAL_CHOICES,
            'CATEGORIA_DOCENTE_CHOICES': Admin_models.CATEGORIA_DOCENTE_CHOICES,
            'GRADO_CIENTIFICO_CHOICES': Admin_models.GRADO_CIENTIFICO_CHOICES,
        }
        
        return render(request, 'Busqueda_Personal/lista_personal.html', contexto)