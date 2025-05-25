from django.shortcuts import render
from django.views import View
from Login import views as Login_views
from django.http import HttpRequest
from Administrador import models as Admin_models

import re
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# Create your views here.

class Registro(View):
    @staticmethod
    def Notificacion(request:HttpRequest,step,Error=None,Success=None):
        if request.user.is_authenticated:
            return Login_views.redirect(request=request)
        return render(request,f'Registro/registro_{step}.html',{
            #2
            'TIPO_CHOICES': Admin_models.TIPO_CHOICES,
            'SEXO_CHOICES': Admin_models.SEXO_CHOICES,
            'COLOR_PIEL_CHOICES': Admin_models.COLOR_PIEL_CHOICES,
            'ESTADO_CIVIL_CHOICES': Admin_models.ESTADO_CIVIL_CHOICES,
            'PROCEDENCIA_SOCIAL_CHOICES': Admin_models.PROCEDENCIA_SOCIAL_CHOICES,
            #3
            'FACULTAD_CHOICES':Admin_models.FACULTAD_CHOICES,
            'DEPARTAMENTO_CHOICES':Admin_models.DEPARTAMENTO_CHOICES,
            'CATEGORIA_DOCENTE_CHOICES':Admin_models.CATEGORIA_DOCENTE_CHOICES,
            'GRADO_CIENTIFICO_CHOICES':Admin_models.GRADO_CIENTIFICO_CHOICES,
            'Error':Error,'Success':Success
        })
    
    def get(self,request:HttpRequest):
        if request.user.is_authenticated:
            return Login_views.redirect(request=request)
        return Registro.Notificacion(request=request,step=1)

    def post(self, request:HttpRequest):
        if request.user.is_authenticated:
            return Login_views.redirect(request=request)
        
        opc = request.POST.get('opc')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')

        if opc in ['1','2',"3_1","3_2"]:
            password2 = request.POST.get('password2')
            v = Validadores.validar_1(username=username,password=password1,password_confirmation=password2,email=email)
            if v == "OK":
                if opc == '1':
                    return Registro.Notificacion(request=request,step=2)
            else:
                return Registro.Notificacion(request=request,step=1,Error=v)
            if opc in ["2","3_1","3_2"]:
                v = Validadores.validar_2(form_data=request.POST)
                if v == "OK":
                    if opc == "2":
                        if request.POST.get('tipo')=='Estudiante':
                            return Registro.Notificacion(request=request,step="3_1")
                        else:
                            return Registro.Notificacion(request=request,step="3_2")
                else:
                    return Registro.Notificacion(request=request,step=2,Error=v)
                    
                if opc == "3_1":
                    facultad = request.POST.get('facultad')
                    if facultad in Admin_models.FACULTAD_CHOICES:
                        user = User(username=username,email=email,tipo_usuario="Estudiante")
                        user.set_password(password1)
                        user.save()
                        get = request.POST.get
                        aspitante = Admin_models.Aspirante.objects.create(
                            userid=user,
                            tipo="Estudiante",nombres=get('nombres'),
                            primer_apellido=get('primer_apellido'),
                            sexo=get('sexo'),
                            ci=get('ci'),
                            lugar_nacimiento=get('lugar_nacimiento'),
                            color_piel=get('color_piel'),
                            estado_civil=get('estado_civil'),
                            ciudadano=get('ciudadano'),
                            procedencia_social=get('procedencia_social'),
                            pais=get('pais'),
                            salario=get('salario'),
                            direccion=get('direccion'),
                            solapin=get('solapin'),
                            segundo_apellido=get('segundo_apellido'),
                            facultad=get('facultad'),
                            telefono=get('telefono'),
                            cargo="Estudiante",
                        )
                        return Login_views.Login.autenticar(request=request,username=username,password=password1)
                    else:
                        return Registro.Notificacion(request=request,step="3_1",Error=f"Valor no válido para 'facultad'. Opciones: {', '.join(map(str, Admin_models.FACULTAD_CHOICES))}")
                    
                elif opc == "3_2":
                    v = Validadores.validar_3_2(datos=request.POST)
                    if v == "OK":
                        user = User(username=username,email=email,tipo_usuario="Estudiante")
                        user.set_password(password1)
                        user.save()
                        get = request.POST.get
                        aspitante = Admin_models.Aspirante.objects.create(
                            userid=user,
                            tipo="Profesor",nombres=get('nombres'),
                            primer_apellido=get('primer_apellido'),
                            sexo=get('sexo'),
                            ci=get('ci'),
                            lugar_nacimiento=get('lugar_nacimiento'),
                            color_piel=get('color_piel'),
                            estado_civil=get('estado_civil'),
                            ciudadano=get('ciudadano'),
                            procedencia_social=get('procedencia_social'),
                            pais=get('pais'),
                            salario=get('salario'),
                            direccion=get('direccion'),
                            solapin=get('solapin'),
                            segundo_apellido=get('segundo_apellido'),
                            facultad=get('facultad'),
                            telefono=get('telefono'),
                            #3
                            cargo=get('cargo'),
                            especialidad=get('especialidad'),
                            centro=get('centro'),
                            ces=get('ces'),
                            departamento=get('departamento'),
                            categoria_docente=get('categoria_docente'),
                            fecha_otorgamiento_categoria=get('fecha_otorgamiento_categoria') or None,
                            grado_cientifico=get('grado_cientifico'),
                            fecha_otorgamiento_grado=get('fecha_otorgamiento_grado') or None,
                        )
                        return Login_views.Login.autenticar(request=request,username=username,password=password1)
                    else:
                        return Registro.Notificacion(request=request,step="3_2",Error=v)
        return Registro.Notificacion(request=request,step=1)
    
    
    




class Validadores:
    @staticmethod
    def validar_1(username, email, password, password_confirmation):
        """
        Valida todos los campos de registro en un solo método
        Retorna 'OK' si todo es válido, o un string con los errores separados por coma
        """
        errores = []
        
        # 1. Validación de username
        if not username:
            errores.append("El nombre de usuario no puede estar vacío")
        elif len(username) < 4:
            errores.append("El nombre de usuario debe tener al menos 4 caracteres")
        elif User.objects.filter(username__iexact=username).exists():
            errores.append("Este nombre de usuario ya está en uso")
        
        # 2. Validación de email
        if not email:
            errores.append("El email no puede estar vacío")
        else:
            try:
                validate_email(email)
            except ValidationError:
                errores.append("El formato del email no es válido")
        
        # 3. Validación de contraseña
        if password != password_confirmation:
            errores.append("Las contraseñas no coinciden")
        
        if len(password) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")
        
        if not any(c.isupper() for c in password):
            errores.append("La contraseña debe contener al menos una letra mayúscula")
        
        if not any(c.islower() for c in password):
            errores.append("La contraseña debe contener al menos una letra minúscula")
        
        if not any(c.isdigit() for c in password):
            errores.append("La contraseña debe contener al menos un número")
        
        caracteres_especiales = "!@#$%^&*()-+?_=,.;:<>/[]{}"
        if not any(c in caracteres_especiales for c in password):
            errores.append("La contraseña debe contener al menos un carácter especial")
        
        # Resultado final
        return "OK" if not errores else ", ".join(errores)
    




    @staticmethod
    def validar_2(form_data):
        errors = []
        
        # Configuration for validation rules
        VALIDATION_CONFIG = {
            'required_fields': [
                'tipo', 'nombres', 'primer_apellido', 'sexo', 'ci',
                'color_piel', 'estado_civil', 'procedencia_social','solapin'
            ],
            'optional_fields': [
                'segundo_apellido', 'lugar_nacimiento', 'ciudadano', 
                'pais', 'salario', 'direccion', 'telefono'
            ],
            'valid_options': {
                'tipo': Admin_models.TIPO_CHOICES,
                'sexo': Admin_models.SEXO_CHOICES,
                'color_piel': Admin_models.COLOR_PIEL_CHOICES,
                'estado_civil': Admin_models.ESTADO_CIVIL_CHOICES,
                'procedencia_social': Admin_models.PROCEDENCIA_SOCIAL_CHOICES
            },
            'regex_patterns': {
                'ci': (r'^\d{11}$', "El CI debe tener exactamente 11 dígitos numéricos"),
                'telefono': (r'^(\+53)?[1-8]\d{6,7}$|^(\+53)?5\d{7}$',
                            "Formato de teléfono inválido. Use +5371234567 o 51234567"),
                'salario': (r'^\d+(\.\d{1,2})?$', "Formato de salario inválido"),
                'nombres': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', "Solo letras y espacios"),
                'primer_apellido': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', "Solo letras y espacios"),
                'segundo_apellido': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]*$', "Solo letras y espacios"),
                'ciudadano': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', "Solo letras y espacios"),
                'pais': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', "Solo letras y espacios"),
                'solapin': (r'^[a-zA-Z0-9]+$', "Solo caracteres alfanuméricos")
            },
            'max_lengths': {
                'nombres': 100, 
                'primer_apellido': 100, 
                'segundo_apellido': 100,
                'ci': 11, 
                'lugar_nacimiento': 100, 
                'ciudadano': 100, 
                'pais': 100,
                'direccion': 500, 
                'telefono': 20, 
                'solapin': 50
            },
            'numeric_ranges': {
                'salario': (1, 999999)  # Minimum 1, maximum 999,999
            },
            'unique_fields': ['ci', 'solapin']  # Campos que deben ser únicos
        }

        # 1. Validate required fields
        for field in VALIDATION_CONFIG['required_fields']:
            value = form_data.get(field, '').strip()
            if not value:
                errors.append(f"El campo '{field}' es obligatorio.")

        # 2. Validate dropdown options
        for field, valid_options in VALIDATION_CONFIG['valid_options'].items():
            value = form_data.get(field, '').strip()
            if value and value not in valid_options:
                errors.append(f"Valor no válido para '{field}'. Opciones válidas: {', '.join(valid_options)}")

        # 3. Validate regex patterns
        for field, (pattern, error_message) in VALIDATION_CONFIG['regex_patterns'].items():
            value = form_data.get(field, '').strip()
            if value and not re.match(pattern, value):
                errors.append(error_message)
                
            # Special CI validation (month and day)
            if field == 'ci' and value and re.match(pattern, value):
                ci_str = str(value)
                month = int(ci_str[2:4])
                day = int(ci_str[4:6])
                
                if not (1 <= month <= 12):
                    errors.append("Los dígitos 3-4 del CI deben indicar mes entre 01 y 12")
                else:
                    days_in_month = {
                        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
                        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
                    }
                    if not (1 <= day <= days_in_month[month]):
                        errors.append(f"Los dígitos 5-6 del CI deben indicar día válido para el mes {month:02d}")

        # 4. Validate field lengths
        for field, max_length in VALIDATION_CONFIG['max_lengths'].items():
            value = form_data.get(field, '').strip()
            if value and len(value) > max_length:
                errors.append(f"El campo '{field}' excede el máximo de {max_length} caracteres")

        # 5. Validate numeric ranges
        for field, (min_val, max_val) in VALIDATION_CONFIG['numeric_ranges'].items():
            value = form_data.get(field, '').strip()
            if value:
                try:
                    numeric_value = float(value)
                    if numeric_value < min_val:
                        errors.append(f"El campo '{field}' no puede ser menor que {min_val}")
                    if numeric_value > max_val:
                        errors.append(f"El campo '{field}' no puede ser mayor que {max_val}")
                except ValueError:
                    errors.append(f"El campo '{field}' debe ser un número válido")
        
        # 6. Validate unique fields (only if all previous validations passed)
        if not errors:
            for field in VALIDATION_CONFIG['unique_fields']:
                value = form_data.get(field, '').strip()
                if value:
                    # Verificar si ya existe un registro con este valor
                    query = Q(**{field: value})
                    if Admin_models.Aspirante.objects.filter(query).exists():
                        errors.append(f"El {field} '{value}' ya está registrado y debe ser único")

        return ', '.join(errors) if errors else "OK"
    

    @staticmethod
    def validar_3_2(datos: dict):
        errores = []
        
        CONFIG = {
            'campos_obligatorios': ['cargo'],
            'opciones_validas': {
                'facultad': Admin_models.FACULTAD_CHOICES,
                'departamento': Admin_models.DEPARTAMENTO_CHOICES,
                'categoria_docente':Admin_models.CATEGORIA_DOCENTE_CHOICES,
                'grado_cientifico': Admin_models.GRADO_CIENTIFICO_CHOICES,
            },
            'validaciones_regex': {
                'especialidad': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', "Solo letras y espacios"),
                'centro': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', "Solo letras y espacios"),
                'cargo': (r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'-]+$', "Solo letras y espacios"),
                'ces': (r'^[a-zA-Z0-9\s]+$', "Solo caracteres alfanuméricos")
            },
            'longitudes_maximas': {
                'especialidad': 100,
                'centro': 100,
                'cargo': 100,
                'ces': 50
            },
            'campos_fecha': [
                'fecha_otorgamiento_categoria',
                'fecha_otorgamiento_grado'
            ]
        }

        # Validación campos obligatorios
        for campo in CONFIG['campos_obligatorios']:
            valor = datos.get(campo)
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                errores.append(f"El campo '{campo}' es obligatorio.")

        # Validación de opciones
        for campo, opciones in CONFIG['opciones_validas'].items():
            valor = datos.get(campo, '')
            if valor and valor not in opciones:
                errores.append(f"Valor no válido para '{campo}'. Opciones: {', '.join(map(str, opciones))}")

        # Validación regex
        for campo, (patron, mensaje) in CONFIG['validaciones_regex'].items():
            valor = datos.get(campo)
            if valor:
                if not re.match(patron, str(valor)):
                    errores.append(mensaje)

        # Validación longitudes
        for campo, max_len in CONFIG['longitudes_maximas'].items():
            valor = datos.get(campo)
            if valor and len(str(valor)) > max_len:
                errores.append(f"El campo '{campo}' excede {max_len} caracteres")

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
            

        # Validaciones de coherencia para campos relacionados
        if bool(datos.get('categoria_docente')) != bool(datos.get('fecha_otorgamiento_categoria')):
            errores.append("La categoría docente y su fecha de otorgamiento deben ir juntas")

        if bool(datos.get('grado_cientifico')) != bool(datos.get('fecha_otorgamiento_grado')):
            errores.append("El grado científico y su fecha de otorgamiento deben ir juntas")

        return 'OK' if not errores else ', '.join(errores) + "."