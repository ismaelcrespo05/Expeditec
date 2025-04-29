from django.shortcuts import render
from django.views import View
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.db.models import Q
from Login import views as Login_views

from django.utils.html import escape
from . import models as Admin_models
from django.utils import timezone
from datetime import datetime

import regex
from . import utils

# Create your views here.

class Dashboard(View):
    def get(self,request:HttpRequest):
        if request.user.is_authenticated:
            return render(request,'Admin/dashboard.html',{
                'Dashboard':True,
            })
        else:
            return Login_views.redirigir_usuario(request)



class Personal(View):
    @staticmethod
    def Notificacion(request:HttpRequest,Error=None,Success=None,back=None):
        if request.user.is_authenticated:
            return render(request,'Admin/personal.html',{
                'Personal':True,'Error':Error,'Success':Success,'back':back
            })
        return Login_views.redirigir_usuario(request)
    
    def get(self, request:HttpRequest):
        if request.user.is_authenticated:
            return render(request,'Admin/personal.html',{
                'Personal':True
            })
        return Login_views.redirigir_usuario(request)
    
    def post(self,request:HttpRequest):
        return Personal.Notificacion(request=request)



class Nuevo_Personal(View):
    def get(self, request):
        return Personal.Notificacion(request=request)
    
    def post(self, request: HttpRequest):
        # Obtener y limpiar datos
        datos = {campo: escape(request.POST.get(campo, '')) 
                for campo in request.POST.keys() 
                if campo != 'csrfmiddlewaretoken'}
        
        # Convertir fechas de string a date
        fecha_cat = datos.get('fecha_otorgamiento_categoria')
        fecha_grado = datos.get('fecha_otorgamiento_grado')
        validacion = Nuevo_Personal.validar_datos_aspirante(datos=datos)
        if validacion != 'OK':
            return Personal.Notificacion(request=request, Error=validacion, back=request.POST)
        try:
            userid = User(username=datos['username'],email=datos['email'])
            password = utils.generar_contraseña()
            userid.set_password(password)
            userid.save()
            # Crear y guardar el aspirante
            aspirante = Admin_models.Aspirante(
                userid = userid,
                tipo=datos['tipo'],  # o 'estudiante' según corresponda
                nombres=datos['nombres'],
                primer_apellido=datos['primer_apellido'],
                segundo_apellido=datos.get('segundo_apellido'),
                sexo=datos['sexo'],
                ci=datos['ci'],
                lugar_nacimiento=datos['lugar_nacimiento'],
                color_piel=datos['color_piel'],
                estado_civil=datos['estado_civil'],
                ciudadano=datos['ciudadano'],
                procedencia_social=datos['procedencia_social'],
                especialidad=datos['especialidad'],
                pais=datos['pais'],
                centro=datos['centro'],
                cargo=datos['cargo'],
                facultad=datos['facultad'],
                ces=datos['ces'],
                departamento=datos['departamento'],
                salario=datos['salario'],
                categoria_docente=datos.get('categoria_docente'),
                direccion=datos['direccion'],
                grado_cientifico=datos.get('grado_cientifico'),
                telefono=datos['telefono'],
                solapin=datos['solapin']
            )
            
            if fecha_cat:
                aspirante.fecha_otorgamiento_categoria = timezone.datetime.strptime(fecha_cat, '%Y-%m-%d').date()
            if fecha_grado:
                aspirante.fecha_otorgamiento_grado = timezone.datetime.strptime(fecha_grado, '%Y-%m-%d').date()
            
            aspirante.save()
            
            return Personal.Notificacion(request=request, Success="Aspirante registrado exitosamente")
        except Exception as e:
            print(e)
            return Personal.Notificacion(request=request, Error="Error al procesar el formulario", back=request.POST)

    @staticmethod
    def validar_datos_aspirante(datos: dict, update=None):
        errores = []

        # Configuración centralizada
        CONFIG = {
            'campos_obligatorios': [
                'tipo', 'nombres', 'primer_apellido', 'segundo_apellido', 'sexo', 'ci',
                'lugar_nacimiento', 'color_piel', 'estado_civil', 'ciudadano',
                'procedencia_social', 'pais',
                'facultad', 'salario', 'categoria_docente',
                'grado_cientifico', 'direccion', 'telefono', 'solapin', 'username', 'email'
            ],
            'opciones_validas': {
                'tipo': Admin_models.TIPO_CHOICES,
                'sexo': Admin_models.SEXO_CHOICES,
                'color_piel': Admin_models.COLOR_PIEL_CHOICES,
                'estado_civil': Admin_models.ESTADO_CIVIL_CHOICES,
                'procedencia_social': Admin_models.PROCEDENCIA_SOCIAL_CHOICES,
                'categoria_docente': Admin_models.CATEGORIA_DOCENTE_CHOICES + ['', 'Ninguna'],
                'grado_cientifico': Admin_models.GRADO_CIENTIFICO_CHOICES + ['', 'Ninguno']
            },
            'validaciones_regex': {
                'ci': (r'^\d{11}$', "El CI debe tener exactamente 11 dígitos"),
                'telefono': (r'^\+?\d{7,20}$', "Formato de teléfono inválido"),
                'salario': (r'^\d+(\.\d{1,2})?$', "Formato de salario inválido"),
                'email': (r'^[\w\.-]+@[\w\.-]+\.\w+$', "Correo electrónico no válido"),
                'nombres': (r'^[\p{L}\s\'-]+$', "El campo 'nombres' solo debe contener letras y espacios"),
                'primer_apellido': (r'^[\p{L}\s\'-]+$', "El campo 'primer apellido' solo debe contener letras y espacios"),
                'segundo_apellido': (r'^[\p{L}\s\'-]*$', "El campo 'segundo apellido' solo debe contener letras y espacios"),
                'lugar_nacimiento': (r'^[\p{L}\s\'-.,]+$', "El campo 'lugar de nacimiento' solo debe contener letras y signos de puntuación básicos"),
                'centro': (r'^[\p{L}\s\'-.,()\d]+$', "El campo 'centro' contiene caracteres no válidos"),
                'facultad': (r'^[\p{L}\s\'-.,()]+$', "El campo 'facultad' contiene caracteres no válidos"),
                'departamento': (r'^[\p{L}\s\'-.,()]+$', "El campo 'departamento' contiene caracteres no válidos"),
                'direccion': (r'^[\p{L}\s\'-.,\d/#]+$', "El campo 'dirección' contiene caracteres no válidos"),
                'ciudadano': (r'^[\p{L}\s]+$', "El campo 'ciudadano' solo debe contener letras y espacios"),
                'pais': (r'^[\p{L}\s]+$', "El campo 'país' solo debe contener letras y espacios"),
                'cargo': (r'^[\p{L}\s\'-.,]+$', "El campo 'cargo' contiene caracteres no válidos"),
                'ces': (r'^[\p{L}\s\'-.,\d]+$', "El campo 'CES' contiene caracteres no válidos"),
                'especialidad': (r'^[\p{L}\s\'-.,]+$', "El campo 'especialidad' contiene caracteres no válidos"),
                'username': (r'^[a-z0-9]+$', "El campo 'username' debe contener solo minúsculas y números, sin espacios"),
            },
            'longitudes_maximas': {
                'nombres': 100, 'primer_apellido': 100, 'segundo_apellido': 100,
                'ci': 11, 'lugar_nacimiento': 100, 'especialidad': 100, 'centro': 100,
                'cargo': 100, 'facultad': 100, 'ces': 100, 'departamento': 100,
                'direccion': 500, 'telefono': 20, 'ciudadano': 100, 'pais': 100, 'email': 100,
                'username': 150, 'solapin': 50
            },
            'campos_fecha': ['fecha_otorgamiento_categoria', 'fecha_otorgamiento_grado']
        }

        # 1. Validar campos obligatorios
        for campo in CONFIG['campos_obligatorios']:
            if not datos.get(campo, '').strip():
                errores.append(f"El campo '{campo}' es obligatorio.")

        # 2. Validar opciones válidas
        for campo, opciones in CONFIG['opciones_validas'].items():
            valor = datos.get(campo)
            if valor and valor not in opciones:
                opciones_validas = [str(op) for op in opciones if op]
                errores.append(f"Valor no válido para '{campo}'. Opciones válidas: {', '.join(opciones_validas)}")

        # 3. Validar formatos usando regex
        for campo, (patron, mensaje) in CONFIG['validaciones_regex'].items():
            valor = datos.get(campo)
            if valor and not regex.match(patron, str(valor)):
                errores.append(mensaje)

        # 4. Validar longitudes máximas
        for campo, max_length in CONFIG['longitudes_maximas'].items():
            valor = datos.get(campo)
            if valor and len(str(valor)) > max_length:
                errores.append(f"El campo '{campo}' excede la longitud máxima de {max_length} caracteres")

        # 5. Validar unicidad del CI y username
        if datos.get('ci') and not any('ci' in e for e in errores):
            queryset = Admin_models.Aspirante.objects.filter(ci=datos['ci'])
            if update:
                queryset = queryset.exclude(pk=update.pk)
            if queryset.exists():
                errores.append("El CI ya está registrado en el sistema")

        if datos.get('username') and not any('username' in e for e in errores):
            queryset = User.objects.filter(username=datos['username'])
            if update:
                queryset = queryset.exclude(pk=update.pk)
            if queryset.exists():
                errores.append("El nombre de usuario ya está registrado en el sistema")

        if datos.get('email') and not any('email' in e for e in errores):
            queryset = User.objects.filter(email=datos['email'])
            if update:
                queryset = queryset.exclude(pk=update.pk)
            if queryset.exists():
                errores.append("El correo electrónico ya está registrado en el sistema")

        # 6. Validar fechas si se proporcionan
        for campo in CONFIG['campos_fecha']:
            valor = datos.get(campo)
            if valor:
                try:
                    fecha = datetime.strptime(valor, '%Y-%m-%d').date()
                    if fecha > datetime.now().date():
                        errores.append(f"La fecha en '{campo}' no puede ser futura")
                except ValueError:
                    errores.append(f"Formato de fecha incorrecto en '{campo}'. Use el formato YYYY-MM-DD.")

        # 7. Validar coherencia entre categoría/grado y sus fechas
        categoria = datos.get('categoria_docente', '')
        fecha_categoria = datos.get('fecha_otorgamiento_categoria')
        
        grado = datos.get('grado_cientifico', '')
        fecha_grado = datos.get('fecha_otorgamiento_grado')

        # Validaciones para categoría docente
        if categoria:
            if categoria.lower() in ['ninguna', 'ninguno', '']:
                if fecha_categoria:
                    errores.append("No puede proporcionar fecha de otorgamiento si la categoría docente es 'Ninguna'")
            elif not fecha_categoria:
                errores.append("Debe proporcionar la fecha de otorgamiento cuando especifica una categoría docente")
        
        if fecha_categoria and (not categoria or categoria.lower() in ['ninguna', 'ninguno', '']):
            errores.append("Debe especificar una categoría docente válida cuando proporciona la fecha de otorgamiento")

        # Validaciones para grado científico
        if grado:
            if grado.lower() in ['ninguno', 'ninguna', '']:
                if fecha_grado:
                    errores.append("No puede proporcionar fecha de otorgamiento si el grado científico es 'Ninguno'")
            elif not fecha_grado:
                errores.append("Debe proporcionar la fecha de otorgamiento cuando especifica un grado científico")
        
        if fecha_grado and (not grado or grado.lower() in ['ninguno', 'ninguna', '']):
            errores.append("Debe especificar un grado científico válido cuando proporciona la fecha de otorgamiento")

        return 'OK' if not errores else ', '.join(errores)+"."






class Busqueda_Personal(View):
    def get(self,request:HttpRequest):
        return Login_views.redirigir_usuario(request=request)
    

    def post(self, request:HttpRequest):
        if request.user.is_authenticated and request.user.is_staff:
            buscar = escape(request.POST.get('buscar').strip())
        
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
            
                return render(request, 'Admin/lista_personal.html', {
                    'aspirantes':aspirantes,'termino_busqueda':buscar,
                    'total_resultados': aspirantes.count(),
                })
            else:
                # Si no hay término de búsqueda, mostrar todos ordenados
                print( Admin_models.Aspirante.objects.all().order_by('nombres', 'primer_apellido'))
                return render(request, 'Admin/lista_personal.html', {
                    'aspirantes': Admin_models.Aspirante.objects.all().order_by('nombres', 'primer_apellido'),
                    'termino_busqueda': '',
                    'total_resultados': Admin_models.Aspirante.objects.count(),
                })
        return Login_views.redirigir_usuario(request=request)
    
