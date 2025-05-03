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
import pandas as pd

import regex
import re
from . import utils


# Create your views here.


class Dashboard(View):
    def get(self,request:HttpRequest):
        if request.user.is_authenticated and request.user.is_staff:
            cant_profesores = Admin_models.Aspirante.objects.filter(tipo='Profesor').count()
            cant_estudiantes = Admin_models.Aspirante.objects.filter(tipo='Estudiante').count()
            cantidad_x_categoria = utils.contar_por_categoria_docente()
            total_usuarios = cant_estudiantes + cant_profesores
            distribucion_x_categoria = {}
            for categoria, cantidad in cantidad_x_categoria.items():
                distribucion_x_categoria[categoria] = round((cantidad / total_usuarios) * 100, 2) if total_usuarios != 0 else 0
            return render(request,'Admin/dashboard.html',{
                'Dashboard':True,'cant_profesores':cant_profesores,'cant_estudiantes':cant_estudiantes,
                'total_personal':total_usuarios,'cantidad_x_categoria':cantidad_x_categoria,
                'distribucion_x_categoria':distribucion_x_categoria
            })
        else:
            return Login_views.redirigir_usuario(request)









###########################################################################################################


class Personal(View):
    @staticmethod
    def Notificacion(request:HttpRequest,Error=None,Success=None,back=None):
        if request.user.is_authenticated and request.user.is_staff:
            return render(request,'Admin/personal.html',{
                'Personal':True,'Error':Error,'Success':Success,'back':back
            })
        return Login_views.redirigir_usuario(request)
    
    def get(self, request:HttpRequest):
        if request.user.is_authenticated and request.user.is_staff:
            return render(request,'Admin/personal.html',{
                'Personal':True
            })
        return Login_views.redirigir_usuario(request)
    
    def post(self,request:HttpRequest):
        return Personal.Notificacion(request=request)



class Nuevo_Personal(View):
    @staticmethod
    def registrar(datos):
        def parse_fecha(fecha_str):
            if fecha_str is None:
                return None
            try:
                # Convertir a string y limpiar
                str_date = str(fecha_str).strip().lower()
                # Verificar valores nulos comunes
                if str_date in ['', 'nan', 'none', 'null', 'na']:
                    return None
                # Parsear la fecha
                return datetime.strptime(str_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return None

        # Creación del usuario
        userid = User(username=datos['username'], email=datos['email'])
        password = utils.generar_contraseña()
        userid.set_password(password)
        userid.save()
        
        # Crear y guardar el aspirante
        aspirante = Admin_models.Aspirante(
            userid=userid,
            tipo=datos['tipo'],
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
            solapin=datos['solapin'],
            # Parseamos las fechas directamente en el constructor
            fecha_otorgamiento_categoria=parse_fecha(datos.get('fecha_otorgamiento_categoria')),
            fecha_otorgamiento_grado=parse_fecha(datos.get('fecha_otorgamiento_grado'))
        )
        
        aspirante.save()
        return aspirante

    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return Personal.Notificacion(request=request)
        else:
            return Login_views.redirigir_usuario(request=request)
    
    def post(self, request: HttpRequest):
        if request.user.is_authenticated and request.user.is_staff:
            # Obtener y limpiar datos
            datos = {campo: escape(request.POST.get(campo, '')) 
                    for campo in request.POST.keys() 
                    if campo != 'csrfmiddlewaretoken'}
            
            # Convertir fechas de string a date
            validacion = Nuevo_Personal.validar_datos_aspirante(datos=datos)
            if validacion != 'OK':
                return Personal.Notificacion(request=request, Error=validacion, back=request.POST)
            try:
                Nuevo_Personal.registrar(datos=datos)
                return Personal.Notificacion(request=request, Success="Aspirante registrado exitosamente")
            except Exception as e:
                print(e)
                return Personal.Notificacion(request=request, Error="Error al procesar el formulario", back=request.POST)
        else:
            return Login_views.redirigir_usuario(request=request)

    @staticmethod
    def validar_datos_aspirante(datos: dict, update=None):
        errores = []
        
        # Configuración centralizada basada en el modelo
        CONFIG = {
            'campos_obligatorios': [
                'tipo', 'nombres', 'primer_apellido', 'sexo', 'ci',
                'lugar_nacimiento', 'color_piel', 'estado_civil', 'ciudadano',
                'procedencia_social', 'pais', 'centro', 'cargo', 'facultad',
                'ces', 'departamento', 'salario', 'direccion', 'telefono', 'solapin',
                'username', 'email'
            ],
            'campos_opcionales': [
                'segundo_apellido', 'categoria_docente', 'fecha_otorgamiento_categoria',
                'grado_cientifico', 'fecha_otorgamiento_grado'
            ],
            'opciones_validas': {
                'tipo': [x[0] for x in Admin_models.Aspirante.TIPO_CHOICES2],
                'sexo': Admin_models.SEXO_CHOICES,
                'color_piel': Admin_models.COLOR_PIEL_CHOICES,
                'estado_civil': Admin_models.ESTADO_CIVIL_CHOICES,
                'procedencia_social': Admin_models.PROCEDENCIA_SOCIAL_CHOICES,
                'categoria_docente': Admin_models.CATEGORIA_DOCENTE_CHOICES + ['', 'Ninguna'],
                'grado_cientifico': Admin_models.GRADO_CIENTIFICO_CHOICES + ['', 'Ninguno']
            },
            'validaciones_regex': {
                'ci': (r'^\d{11}$', "El CI debe tener exactamente 11 dígitos"),
                'telefono': (r'^(\+53)?[1-8]\d{6,7}$|^(\+53)?5\d{7}$', 
                            "Formato de teléfono inválido. Use +5371234567 o 51234567"),
                'salario': (r'^\d+(\.\d{1,2})?$', "Formato de salario inválido"),
                'email': (r'^[\w\.-]+@[\w\.-]+\.\w+$', "Correo electrónico no válido"),
                'nombres': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', "Solo letras y espacios"),
                'primer_apellido': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', "Solo letras y espacios"),
                'segundo_apellido': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]*$', "Solo letras y espacios"),
                'ciudadano': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', "Solo letras y espacios"),
                'pais': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', "Solo letras y espacios"),
                'solapin': (r'^[a-zA-Z0-9]+$', "Solo caracteres alfanuméricos")
            },
            'longitudes_maximas': {
                'nombres': 100, 'primer_apellido': 100, 'segundo_apellido': 100,
                'ci': 11, 'lugar_nacimiento': 100, 'especialidad': 100, 'centro': 100,
                'cargo': 100, 'facultad': 100, 'ces': 100, 'departamento': 100,
                'direccion': 500, 'telefono': 20, 'ciudadano': 100, 'pais': 100, 
                'email': 100, 'username': 150, 'solapin': 50
            },
            'campos_fecha': ['fecha_otorgamiento_categoria', 'fecha_otorgamiento_grado'],
            'campos_unique': ['ci', 'solapin', 'username', 'email']
        }

        # 1. Validar campos obligatorios (excepto para actualización si no se envían)
        for campo in CONFIG['campos_obligatorios']:
            valor = datos.get(campo)    
            
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                errores.append(f"El campo '{campo}' es obligatorio.")

        # 2. Validar opciones válidas
        for campo, opciones in CONFIG['opciones_validas'].items():
            valor = datos.get(campo)
            if valor not in opciones:
                opciones_validas = [str(op) for op in opciones]
                errores.append(f"Valor no válido para '{campo}'. Opciones válidas: {', '.join(opciones_validas)}")

        # 3. Validar formatos usando regex
        for campo, (patron, mensaje) in CONFIG['validaciones_regex'].items():
            valor = datos.get(campo)
            if valor and not re.match(patron, str(valor)):
                errores.append(mensaje)

        # 4. Validar longitudes máximas
        for campo, max_length in CONFIG['longitudes_maximas'].items():
            valor = datos.get(campo)
            if valor and len(str(valor)) > max_length:
                errores.append(f"El campo '{campo}' excede la longitud máxima de {max_length} caracteres")

        # 5. Validar unicidad de campos únicos
        for campo in CONFIG['campos_unique']:
            valor = datos.get(campo)
            queryset = None
            if valor:
                if campo in ['username', 'email']:
                    queryset = User.objects.filter(**{campo: valor})
                    if not update is None:
                        queryset = queryset.exclude(pk=update.userid.pk)
                else:
                    queryset = Admin_models.Aspirante.objects.filter(**{campo: valor})
                    if not update is None:
                        queryset = queryset.exclude(pk=update.pk)
                        
                if queryset.exists():
                    errores.append(f"El {campo} '{valor}' ya está registrado")

        # 6. Validar fechas
        for campo in CONFIG['campos_fecha']:
            valor = datos.get(campo)
            if not valor in ['','nan','None']:
                try:
                    fecha = datetime.strptime(valor, '%Y-%m-%d').date()
                    if fecha > datetime.now().date():
                        errores.append(f"La fecha en '{campo}' no puede ser futura")
                except ValueError:
                    errores.append(f"Formato de fecha incorrecto en '{campo}'. Use YYYY-MM-DD")
            else:
                datos[campo] = None

        # 7. Validar coherencia entre categoría/grado y sus fechas
        categoria = datos.get('categoria_docente', '')
        fecha_categoria = datos.get('fecha_otorgamiento_categoria')
        grado = datos.get('grado_cientifico', '')
        fecha_grado = datos.get('fecha_otorgamiento_grado')

        # Validación para categoría docente
        if categoria and categoria.lower() not in ['ninguna', 'ninguno', '']:
            if not fecha_categoria:
                errores.append("Debe proporcionar fecha de otorgamiento para la categoría docente")
        elif fecha_categoria:
            errores.append("No puede tener fecha de categoría sin especificar una categoría válida")

        # Validación para grado científico
        if grado and grado.lower() not in ['ninguno', 'ninguna', '']:
            if not fecha_grado:
                errores.append("Debe proporcionar fecha de otorgamiento para el grado científico")
        elif fecha_grado:
            errores.append("No puede tener fecha de grado sin especificar un grado válido")

        return 'OK' if not errores else ', '.join(errores) + "."






class Personal_CSV(View):
    def get(self,request):
        return Personal.Notificacion(request=request)
    
    def post(self, request: HttpRequest):
        if request.user.is_authenticated and request.user.is_staff:
            # Verificar si se envió un archivo
            if 'csv_file' not in request.FILES:
                return Personal.Notificacion(request=request, Error='No se encontró archivo CSV')
            
            csv_file = request.FILES['csv_file']
            
            # Validar extensión del archivo
            if not csv_file.name.endswith('.csv'):
                return Personal.Notificacion(request=request, Error='El archivo debe ser un CSV')
            
            try:
                # Leer el archivo CSV con pandas
                df = pd.read_csv(csv_file, dtype=str)
                
                # Convertir todas las columnas a string
                df = df.astype(str)
                
                # Verificar que existe la columna CI
                if 'ci' not in df.columns:
                    return Personal.Notificacion(request=request, Error='El CSV debe contener una columna "ci"')
                
                # Obtener lista de CIs válidos del CSV (ya son strings)
                cis_en_csv = df['ci'].replace('nan', '').replace('None', '').str.strip().unique().tolist()
                cis_en_csv = [ci for ci in cis_en_csv if ci]  # Eliminar strings vacíos
                
                # Contadores para resultados
                registros_actualizados = 0
                registros_creados = 0
                registros_con_error = 0
                errores_detallados = []
                
                # Procesar cada fila del CSV
                for index, row in df.iterrows():
                    try:
                        row_dict = row.to_dict()
                        ci = row_dict.get('ci', '').strip()
                        
                        if not ci:
                            registros_con_error += 1
                            errores_detallados.append(f"Fila {index+1}: CI vacío/inválido")
                            continue

                        
                        

                        if Admin_models.Aspirante.objects.filter(ci=ci).exists():
                            asp_old = Admin_models.Aspirante.objects.get(ci=ci)
                            validacion = Nuevo_Personal.validar_datos_aspirante(datos=row_dict, update=asp_old)
                            if validacion == 'OK':
                                # Actualizar campos (todos convertidos a string)
                                asp_old.tipo = row_dict.get('tipo', '')
                                asp_old.nombres = row_dict.get('nombres', '')
                                asp_old.primer_apellido = row_dict.get('primer_apellido', '')
                                asp_old.segundo_apellido = row_dict.get('segundo_apellido', '')
                                asp_old.sexo = row_dict.get('sexo', '')
                                asp_old.lugar_nacimiento = row_dict.get('lugar_nacimiento', '')
                                asp_old.color_piel = row_dict.get('color_piel', '')
                                asp_old.estado_civil = row_dict.get('estado_civil', '')
                                asp_old.ciudadano = row_dict.get('ciudadano', '')
                                asp_old.procedencia_social = row_dict.get('procedencia_social', '')
                                asp_old.especialidad = row_dict.get('especialidad', '')
                                asp_old.pais = row_dict.get('pais', '')
                                asp_old.cargo = row_dict.get('cargo', '')
                                asp_old.facultad = row_dict.get('facultad', '')
                                asp_old.ces = row_dict.get('ces', '')
                                asp_old.departamento = row_dict.get('departamento', '')
                                asp_old.salario = row_dict.get('salario', '')
                                asp_old.categoria_docente = row_dict.get('categoria_docente', '')
                                asp_old.fecha_otorgamiento_categoria = row_dict.get('fecha_otorgamiento_categoria', '')
                                asp_old.direccion = row_dict.get('direccion', '')
                                asp_old.grado_cientifico = row_dict.get('grado_cientifico', '')
                                asp_old.fecha_otorgamiento_grado = row_dict.get('fecha_otorgamiento_grado', '')
                                asp_old.telefono = row_dict.get('telefono', '')
                                asp_old.solapin = row_dict.get('solapin', '')
                                asp_old.save()
                                registros_actualizados += 1
                            else:
                                registros_con_error += 1
                                errores_detallados.append(f"Fila {index+1}: {validacion}")
                        else:
                            
                            validacion = Nuevo_Personal.validar_datos_aspirante(datos=row_dict)
                            if validacion == 'OK':
                                nuevo_aspirante = Nuevo_Personal.registrar(datos=row_dict)
                                if nuevo_aspirante:
                                    registros_creados += 1
                                else:
                                    registros_con_error += 1
                                    errores_detallados.append(f"Fila {index+1}: Error al crear registro")
                            else:
                                registros_con_error += 1
                                errores_detallados.append(f"Fila {index+1}: {validacion}") 
                    except Exception as e:
                        registros_con_error += 1
                        errores_detallados.append(f"Fila {index+1}: Error - {str(e)}")
                
                # Eliminar aspirantes que NO están en el CSV
                aspirantes_a_eliminar = Admin_models.Aspirante.objects.exclude(ci__in=cis_en_csv)
                
                cantidad_eliminados = aspirantes_a_eliminar.count()
                for userids in aspirantes_a_eliminar:
                    userids.userid.delete()
                
                # Construir mensaje en un solo string
                mensaje = (
                    f"Proceso completado. "
                    f"Actualizados: {registros_actualizados}, "
                    f"Creados: {registros_creados}, "
                    f"Eliminados: {cantidad_eliminados}, "
                    f"Errores: {registros_con_error}"
                )
                
                # Agregar detalles de errores si existen
                if errores_detallados:
                    mensaje += ". Errores: " + ", ".join(errores_detallados[:5])  # Mostrar primeros 5 errores
                
                return Personal.Notificacion(
                    request=request,
                    Success=mensaje
                )
            
            except pd.errors.EmptyDataError:
                return Personal.Notificacion(request=request, Error='El archivo CSV está vacío')
            except pd.errors.ParserError:
                return Personal.Notificacion(request=request, Error='Error al leer el archivo CSV')
            except Exception as e:
                return Personal.Notificacion(request=request, Error=f'Error inesperado: {str(e)}')
        else:
            return Login_views.redirigir_usuario(request)    

