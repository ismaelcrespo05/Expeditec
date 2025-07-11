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
from Chat import models as Chat_models
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
        userid = User(username=datos['username'], email=datos['email'],tipo_usuario='Aspirante')
        password = utils.generar_contraseña()
        userid.set_password(password)
        userid.save()
        
        # Crear y guardar el aspirante
        aspirante = Admin_models.Aspirante(
            userid=userid,
            tipo=datos.get('tipo'),
            nombres=datos.get('nombres'),
            primer_apellido=datos.get('primer_apellido'),
            segundo_apellido=datos.get('segundo_apellido'),
            sexo=datos.get('sexo'),
            ci=datos.get('ci'),
            lugar_nacimiento=datos.get('lugar_nacimiento'),
            color_piel=datos.get('color_piel'),
            estado_civil=datos.get('estado_civil'),
            ciudadano=datos.get('ciudadano'),
            procedencia_social=datos.get('procedencia_social'),
            especialidad=datos.get('especialidad'),
            pais=datos.get('pais'),
            centro=datos.get('centro'),
            cargo=datos.get('cargo'),
            facultad=datos.get('facultad'),
            ces=datos.get('ces'),
            departamento=datos.get('departamento'),
            salario=datos.get('salario'),
            categoria_docente=datos.get('categoria_docente'),
            direccion=datos.get('direccion'),
            grado_cientifico=datos.get('grado_cientifico'),
            telefono=datos.get('telefono'),
            solapin=datos.get('solapin'),
            area=datos.get('area'),
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
    def validar_datos_aspirante(datos: dict, update=None):  # update: instancia de Aspirante para edición
        errores = []

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
                'ci': (r'^\d{11}$', "El CI debe tener exactamente 11 dígitos numéricos"),
                'telefono': (r'^(\+53)?[1-8]\d{6,7}$|^(\+53)?5\d{7}$',
                            "Formato de teléfono inválido. Use +5371234567 o 51234567"),
                'salario': (r'^\d+(\.\d{1,2})?$', "Formato de salario inválido"),
                'email': (r'^[\w\.-]+@[\w\.-]+\.\w+$', "Correo electrónico no válido"),
                'nombres': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', "Solo letras y espacios"),
                'primer_apellido': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', "Solo letras y espacios"),
                'segundo_apellido': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]*$', "Solo letras y espacios"),
                'ciudadano': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', "Solo letras y espacios"),
                'pais': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', "Solo letras y espacios"),
                'area': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', "Solo letras y espacios"),
                'solapin': (r'^[a-zA-Z0-9]+$', "Solo caracteres alfanuméricos")
            },
            'longitudes_maximas': {
                'nombres': 100, 'primer_apellido': 100, 'segundo_apellido': 100,
                'ci': 11, 'lugar_nacimiento': 100, 'especialidad': 100, 'centro': 100,
                'cargo': 100, 'facultad': 100, 'ces': 100, 'departamento': 100,
                'direccion': 500, 'telefono': 20, 'ciudadano': 100, 'pais': 100,
                'email': 100, 'username': 150, 'solapin': 50, 'area': 100
            },
            'campos_fecha': ['fecha_otorgamiento_categoria', 'fecha_otorgamiento_grado'],
            'campos_unique': ['ci', 'solapin', 'username', 'email']
        }

        tipo = datos.get('tipo', '').strip().lower()

        # Validación campos obligatorios
        for campo in CONFIG['campos_obligatorios']:
            valor = datos.get(campo)
            if update is not None and valor is None:
                continue
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                errores.append(f"El campo '{campo}' es obligatorio.")

        # Validación de opciones
        for campo, opciones in CONFIG['opciones_validas'].items():
            valor = datos.get(campo, '')
            if valor not in opciones:
                errores.append(f"Valor no válido para '{campo}'. Opciones: {', '.join(map(str, opciones))}")

        # Validación regex
        for campo, (patron, mensaje) in CONFIG['validaciones_regex'].items():
            valor = datos.get(campo)
            if valor:
                if not re.match(patron, str(valor)):
                    errores.append(mensaje)
                elif campo == 'ci':
                    ci_str = str(valor)
                    mes = int(ci_str[2:4])
                    dia = int(ci_str[4:6])
                    if not (1 <= mes <= 12):
                        errores.append("Los dígitos 3-4 del CI deben indicar mes entre 01 y 12")
                    else:
                        dias_por_mes = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30,
                                        7:31, 8:31, 9:30,10:31,11:30,12:31}
                        if not (1 <= dia <= dias_por_mes[mes]):
                            errores.append(f"Los dígitos 5-6 del CI deben indicar día válido para el mes {mes:02d}")

        # Validación longitudes
        for campo, max_len in CONFIG['longitudes_maximas'].items():
            valor = datos.get(campo)
            if valor and len(str(valor)) > max_len:
                errores.append(f"El campo '{campo}' excede {max_len} caracteres")

        # Validación de unicidad
        for campo in CONFIG['campos_unique']:
            valor = datos.get(campo)
            if valor:
                if campo in ['username', 'email']:
                    qs = User.objects.filter(**{campo: valor})
                    if update is not None:
                        qs = qs.exclude(pk=update.userid.pk)
                else:
                    qs = Admin_models.Aspirante.objects.filter(**{campo: valor})
                    if update is not None:
                        qs = qs.exclude(pk=update.pk)
                if qs.exists():
                    errores.append(f"El {campo} '{valor}' ya está registrado")

        # Validación fechas
        for campo in CONFIG['campos_fecha']:
            valor = datos.get(campo)
            if valor not in [None, '', 'nan']:
                try:
                    f = datetime.strptime(valor, '%Y-%m-%d').date()
                    if f > datetime.now().date():
                        errores.append(f"La fecha en '{campo}' no puede ser futura")
                except ValueError:
                    errores.append(f"Formato incorrecto en '{campo}'. Use YYYY-MM-DD")
            else:
                datos[campo] = None

        # Coherencia entre tipo y campos docentes
        if tipo == 'profesor':
            if not datos.get('categoria_docente') or datos.get('categoria_docente') == 'Ninguna':
                errores.append("Profesores deben especificar una 'categoria_docente' válida distinta de 'Ninguna'")
            if not datos.get('fecha_otorgamiento_categoria'):
                errores.append("Profesores deben especificar 'fecha_otorgamiento_categoria'")
            if not datos.get('grado_cientifico') or datos.get('grado_cientifico') == 'Ninguno':
                errores.append("Profesores deben especificar un 'grado_cientifico' válido distinto de 'Ninguno'")
            if not datos.get('fecha_otorgamiento_grado'):
                errores.append("Profesores deben especificar 'fecha_otorgamiento_grado'")

            # Validaciones cruzadas de campos docentes
            if datos.get('categoria_docente'):
                if not datos.get('fecha_otorgamiento_categoria'):
                    errores.append("Debe proporcionar fecha para 'categoria_docente'")
            if datos.get('fecha_otorgamiento_categoria'):
                if not datos.get('categoria_docente') or datos.get('categoria_docente') == 'Ninguna':
                    errores.append("No puede tener fecha de categoría sin categoría válida")
            if datos.get('grado_cientifico'):
                if not datos.get('fecha_otorgamiento_grado'):
                    errores.append("Debe proporcionar fecha para 'grado_cientifico'")
            if datos.get('fecha_otorgamiento_grado'):
                if not datos.get('grado_cientifico') or datos.get('grado_cientifico') == 'Ninguno':
                    errores.append("No puede tener fecha de grado sin grado válido")

        elif tipo == 'estudiante':
            if datos.get('categoria_docente') and datos.get('categoria_docente') != 'Ninguna':
                errores.append("Estudiantes solo pueden tener 'categoria_docente' con valor 'Ninguna'")
            if datos.get('grado_cientifico') and datos.get('grado_cientifico') != 'Ninguno':
                errores.append("Estudiantes solo pueden tener 'grado_cientifico' con valor 'Ninguno'")
            if datos.get('fecha_otorgamiento_categoria') not in [None, '', 'nan']:
                errores.append("Estudiantes no deben tener 'fecha_otorgamiento_categoria'")
            if datos.get('fecha_otorgamiento_grado') not in [None, '', 'nan']:
                errores.append("Estudiantes no deben tener 'fecha_otorgamiento_grado'")

        
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
                                asp_old.area = row_dict.get('area','')
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





class Personal_RRHH(View):
    @staticmethod
    def Notificacion(request: HttpRequest, Error=None, Success=None):
        if request.user.is_authenticated and request.user.is_staff:
            # Obtener todos los usuarios de RRHH
            personal_rrhh = User.objects.filter(
                id__in=Admin_models.RRHH.objects.all().values('userid_id')
            ).order_by('-date_joined')
            
            return render(request, 'Admin/personal_rrhh.html', {
                'personal_rrhh': personal_rrhh,
                'Error': Error,
                'Success': Success,
                'Personal_RRHH':True
            })
        else:
            return Login_views.redirigir_usuario(request)

    def get(self, request: HttpRequest):
        if request.user.is_authenticated and request.user.is_staff:
            # Obtener todos los usuarios de RRHH con información adicional
            rrhh_users = Admin_models.RRHH.objects.all().select_related('userid')
            
            # Crear lista con los datos que necesitamos mostrar
            personal_rrhh = []
            for rrhh in rrhh_users:
                user = rrhh.userid
                personal_rrhh.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'last_login': user.last_login,
                    'date_joined': user.date_joined,
                    'is_active': user.is_active
                })
            
            return render(request, 'Admin/personal_rrhh.html', {
                'personal_rrhh': personal_rrhh,
                'Personal_RRHH':True
            })
        else:
            return Login_views.redirigir_usuario(request)

    def post(self, request: HttpRequest):
        if request.user.is_staff:
            username = request.POST.get('username')
            email = request.POST.get('email')
            
            # Validar que el usuario no exista
            if User.objects.filter(username=username).exists():
                return self.Notificacion(
                    request=request,
                    Error='El nombre de usuario ya está en uso'
                )
            
            #if User.objects.filter(email=email).exists():
            #    return self.Notificacion(
            #        request=request,
            #        Error='El correo electrónico ya está registrado'
            #    )
            
            try:
                # Crear nuevo usuario
                nuevo_usuario = User(
                    username=username,
                    email=email,
                    is_staff=False,  # No es staff para que no tenga acceso a todo
                    tipo_usuario="RRHH"
                )
                pass1 = utils.generar_contraseña()
                nuevo_usuario.set_password(pass1)
                nuevo_usuario.save()
                
                # Asignar al modelo RRHH
                Admin_models.RRHH.objects.create(userid=nuevo_usuario)
                
                chats = Chat_models.Chat.objects.all()
                for ch in chats:
                    Chat_models.Miembro_Chat.objects.create(
                        chat_id=ch,
                        userid=nuevo_usuario,
                        tipo="RRHH"
                    )


                # Opcional: Enviar correo con credenciales
                # utils.enviar_credenciales(email, username, pass1)
                
                return self.Notificacion(
                    request=request,
                    Success=f'Usuario {username} creado con éxito.'
                )
            except Exception as e:
                return self.Notificacion(
                    request=request,
                    Error=f'Error al crear usuario: {str(e)}'
                )
        else:
            return Login_views.redirigir_usuario(request)
        



def delete_personal_rrhh(request):
    if request.POST:
        user_id = request.POST.get('user_id')
        try:
            userid = User.objects.get(id=user_id)
            user_rh = Admin_models.RRHH.objects.get(userid=userid)
            userid.delete()
            return Personal_RRHH.Notificacion(
                request=request,
                Success='Usuario eliminado correctamente'
            )
        except Exception as e:
            return Personal_RRHH.Notificacion(
                request=request,
                Error=f'Error al eliminar el usuario: {str(e)}'
            )
    else:
        return Login_views.redirigir_usuario(request)
    



class Editar_Aspirante(View):
    @staticmethod
    def Notificacion(request:HttpRequest,aspirante_id:int,Error=None,Success=None):
        if request.user.is_staff:
            try:
                aspirante = Admin_models.Aspirante.objects.get(id=aspirante_id)
                return render(request,'Admin/edit_personal.html',{
                    'aspirante':aspirante,'Error':Error,'Success':Success
                })
            except Exception as e:
                print(e)
        return Login_views.redirigir_usuario(request=request)
            

    def get(self,request:HttpRequest,aspirante_id:int):
        if request.user.is_staff:
            try:
                aspirante = Admin_models.Aspirante.objects.get(id=aspirante_id)
                return render(request,'Admin/edit_personal.html',{
                    'aspirante':aspirante
                })
            except Exception as e:
                print(e)
        return Login_views.redirigir_usuario(request=request)
            


    def post(self, request:HttpRequest,aspirante_id:int):
        if request.user.is_staff:
            if Admin_models.Aspirante.objects.filter(id=aspirante_id).exists():
                asp_old = Admin_models.Aspirante.objects.get(id=aspirante_id)
                validacion = Nuevo_Personal.validar_datos_aspirante(datos=request.POST, update=asp_old)
                if validacion == 'OK':
                    # Actualizar campos (todos convertidos a string)
                    asp_old.tipo = request.POST.get('tipo', '')
                    asp_old.nombres = request.POST.get('nombres', '')
                    asp_old.primer_apellido = request.POST.get('primer_apellido', '')
                    asp_old.segundo_apellido = request.POST.get('segundo_apellido', '')
                    asp_old.sexo = request.POST.get('sexo', '')
                    asp_old.lugar_nacimiento = request.POST.get('lugar_nacimiento', '')
                    asp_old.color_piel = request.POST.get('color_piel', '')
                    asp_old.estado_civil = request.POST.get('estado_civil', '')
                    asp_old.ciudadano = request.POST.get('ciudadano', '')
                    asp_old.procedencia_social = request.POST.get('procedencia_social', '')
                    asp_old.especialidad = request.POST.get('especialidad', '')
                    asp_old.pais = request.POST.get('pais', '')
                    asp_old.cargo = request.POST.get('cargo', '')
                    asp_old.facultad = request.POST.get('facultad', '')
                    asp_old.ces = request.POST.get('ces', '')
                    asp_old.departamento = request.POST.get('departamento', '')
                    asp_old.salario = request.POST.get('salario', '')
                    asp_old.categoria_docente = request.POST.get('categoria_docente', '')
                    asp_old.fecha_otorgamiento_categoria = request.POST.get('fecha_otorgamiento_categoria', '')
                    asp_old.direccion = request.POST.get('direccion', '')
                    asp_old.grado_cientifico = request.POST.get('grado_cientifico', '')
                    asp_old.fecha_otorgamiento_grado = request.POST.get('fecha_otorgamiento_grado', '')
                    asp_old.telefono = request.POST.get('telefono', '')
                    asp_old.solapin = request.POST.get('solapin', '')
                    asp_old.area = request.POST.get('area','')
                    asp_old.userid.username=request.POST.get('username')
                    asp_old.userid.email=request.POST.get('email')
                    asp_old.userid.save()
                    asp_old.save()
                    return Editar_Aspirante.Notificacion(request=request,aspirante_id=aspirante_id,Success="Aspirante actualizado correctamente.")
                else:
                    return Editar_Aspirante.Notificacion(request=request,aspirante_id=aspirante_id,Error=validacion)
        return Login_views.redirigir_usuario(request=request)
        