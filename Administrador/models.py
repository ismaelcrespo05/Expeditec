from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from datetime import datetime
import re

User.add_to_class('tipo_usuario', models.TextField(null=True))


# Definición de choices (se mantienen como listas de strings para mejor legibilidad)
TIPO_CHOICES = ['Profesor', 'Estudiante']
SEXO_CHOICES = ['Masculino', 'Femenino']
COLOR_PIEL_CHOICES = ['Blanca', 'Negra']
ESTADO_CIVIL_CHOICES = ['Soltero/a', 'Casado/a', 'Divorciado/a', 'Viudo/a']
PROCEDENCIA_SOCIAL_CHOICES = ['Obrera', 'Campesina']
FACULTAD_CHOICES = [
    'Facultad de Ciberseguridad',
    'Facultad de Informática Organizacional',
    'Facultad de Tecnologías Interactivas',
    'Facultad de Ciencias y Tecnologías Computacionales',
    'Facultad de Tecnologías Educativas',
    'Facultad de Tecnologías Libres'
]
DEPARTAMENTO_CHOICES = [
    'Departamento de Infraestructura Tecnológica',
    'Departamento de Ciberseguridad',
    'Departamento de Física',
    'Departamento de Informática',
    'Departamento de Gestión Organizacional',
    'Departamento de Inteligencia Computacional',
    'Departamento de Bioinformática',
    'Centro de Idiomas',
    'Departamento de Marxismo Leninismo e Historia',
    'Departamento de Enseñanza Militar'
]
CATEGORIA_DOCENTE_CHOICES = [
    'ATD Medio Superior',
    'ATD Superior',
    'Instructor',
    'Profesor Asistente',
    'Profesor Auxiliar',
    'Profesor Titular'
]
GRADO_CIENTIFICO_CHOICES = ['Máster', 'Doctor']

class Aspirante(models.Model):
    userid = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    
    # Campos principales
    tipo = models.CharField(
        max_length=10,
        verbose_name='Tipo de aspirante',
        choices=[(tipo, tipo) for tipo in TIPO_CHOICES],
        null=False,
    )
    
    nombres = models.CharField(max_length=100, verbose_name='Nombres', null=False)
    primer_apellido = models.CharField(max_length=100, verbose_name='Primer apellido', null=False)
    segundo_apellido = models.CharField(
        max_length=100, 
        verbose_name='Segundo apellido', 
        blank=True, 
        null=True,
    )
    sexo = models.CharField(
        max_length=10, 
        verbose_name='Sexo',
        choices=[(sexo, sexo) for sexo in SEXO_CHOICES],
        null=False
    )
    ci = models.CharField(
        max_length=11, 
        unique=True, 
        verbose_name='Carné de identidad',
        null=False,
        validators=[
            RegexValidator(
                regex=r'^\d{11}$',
                message='El CI debe tener exactamente 11 dígitos numéricos'
            )
        ]
    )
    lugar_nacimiento = models.CharField(
        max_length=100, 
        verbose_name='Lugar de nacimiento',
        null=False
    )
    color_piel = models.CharField(
        max_length=10,
        verbose_name='Color de piel',
        choices=[(color, color) for color in COLOR_PIEL_CHOICES],
        null=False
    )
    estado_civil = models.CharField(
        max_length=12, 
        verbose_name='Estado civil',
        choices=[(estado, estado) for estado in ESTADO_CIVIL_CHOICES],
        null=False
    )
    ciudadano = models.CharField(
        max_length=100, 
        verbose_name='Ciudadano',
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
                message='Solo se permiten letras y espacios'
            )
        ]
    )
    procedencia_social = models.CharField(
        max_length=15, 
        verbose_name='Procedencia social',
        choices=[(procedencia, procedencia) for procedencia in PROCEDENCIA_SOCIAL_CHOICES],
        null=False
    )
    especialidad = models.CharField(
        max_length=100, 
        verbose_name='Especialidad',
        null=False
    )
    pais = models.CharField(
        max_length=100, 
        verbose_name='País',
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
                message='Solo se permiten letras y espacios'
            )
        ]
    )
    centro = models.CharField(
        max_length=100, 
        verbose_name='Centro de trabajo/estudio',
        null=False
    )
    cargo = models.CharField(
        max_length=100, 
        verbose_name='Cargo',
        blank=True,
        null=True
    )
    facultad = models.CharField(
        max_length=50, 
        verbose_name='Facultad',
        choices=[(facultad, facultad) for facultad in FACULTAD_CHOICES],
        blank=True,
        null=True
    )
    ces = models.CharField(
        max_length=100, 
        verbose_name='CES',
        blank=True,
        null=True
    )
    departamento = models.CharField(
        max_length=50, 
        verbose_name='Departamento',
        choices=[(departamento, departamento) for departamento in DEPARTAMENTO_CHOICES],
        blank=True,
        null=True
    )
    salario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[
            MinValueValidator(1),
            MaxValueValidator(999999.99)
        ],
        verbose_name='Salario',
        null=False
    )
    categoria_docente = models.CharField(
        max_length=30, 
        blank=True, 
        null=True,
        verbose_name='Categoría docente',
        choices=[(categoria, categoria) for categoria in CATEGORIA_DOCENTE_CHOICES]
    )
    fecha_otorgamiento_categoria = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Fecha de otorgamiento de categoría'
    )
    direccion = models.TextField(
        max_length=500,
        verbose_name='Dirección particular',
        null=False
    )
    grado_cientifico = models.CharField(
        max_length=10, 
        blank=True,
        null=True,
        verbose_name='Grado científico',
        choices=[(grado, grado) for grado in GRADO_CIENTIFICO_CHOICES]
    )
    fecha_otorgamiento_grado = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Fecha de otorgamiento de grado científico'
    )
    telefono = models.CharField(
        max_length=20, 
        verbose_name='Teléfono',
        null=False,
        validators=[
            RegexValidator(
                regex=r'^(\+53)?[1-8]\d{6,7}$|^(\+53)?5\d{7}$',
                message='Formato de teléfono inválido. Use +5371234567 o 51234567'
            )
        ]
    )
    solapin = models.CharField(
        max_length=50, 
        verbose_name='Solapín',
        null=False,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message='Solo caracteres alfanuméricos'
            )
        ]
    )

    class Meta:
        verbose_name = 'Aspirante'
        verbose_name_plural = 'Aspirantes'
        ordering = ['nombres', 'primer_apellido']
    
    def clean(self):
        super().clean()
        # Validación de CI (mes y día)
        if self.ci and len(self.ci) == 11:
            try:
                mes = int(self.ci[2:4])
                dia = int(self.ci[4:6])
                if not (1 <= mes <= 12):
                    raise ValidationError({'ci': "Los dígitos 3-4 del CI deben indicar mes entre 01 y 12"})
                
                dias_por_mes = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
                if not (1 <= dia <= dias_por_mes.get(mes, 31)):
                    raise ValidationError({'ci': f"Los dígitos 5-6 del CI deben indicar día válido para el mes {mes:02d}"})
            except ValueError:
                pass
        
        # Validaciones específicas por tipo
        if self.tipo == 'Estudiante':
            if not self.facultad:
                raise ValidationError({'facultad': "Para estudiantes, el campo 'facultad' es obligatorio"})
            
            if self.categoria_docente or self.fecha_otorgamiento_categoria or self.grado_cientifico or self.fecha_otorgamiento_grado:
                raise ValidationError("Estudiantes no deben tener valores en campos docentes")
            
            self.cargo = 'Estudiante'
        
        elif self.tipo == 'Profesor':
            if not self.cargo:
                raise ValidationError({'cargo': "Para profesores, el campo 'cargo' es obligatorio"})
            
            # Validar que categoría docente y fecha vayan juntas
            if bool(self.categoria_docente) != bool(self.fecha_otorgamiento_categoria):
                raise ValidationError("La categoría docente y su fecha de otorgamiento deben ir juntas")
            
            # Validar que grado científico y fecha vayan juntas
            if bool(self.grado_cientifico) != bool(self.fecha_otorgamiento_grado):
                raise ValidationError("El grado científico y su fecha de otorgamiento deben ir juntas")

    def __str__(self):
        return f"{self.grado_cientifico or ''} {self.nombres} {self.primer_apellido} {self.segundo_apellido or ''} ({self.get_tipo_display()}{f' {self.categoria_docente}' if self.categoria_docente else ''})"





    @staticmethod
    def validar_datos_aspirante(datos: dict, update=None):
        errores = []

        CONFIG = {
            'campos_obligatorios_generales': [
                'tipo', 'nombres', 'primer_apellido', 'sexo', 'ci',
                'lugar_nacimiento', 'color_piel', 'estado_civil', 'ciudadano',
                'procedencia_social', 'pais', 'salario', 'direccion', 'solapin'
            ],
            'campos_opcionales_generales': [
                'segundo_apellido', 'facultad', 'ces', 'departamento', 
                'categoria_docente', 'fecha_otorgamiento_categoria',
                'grado_cientifico', 'fecha_otorgamiento_grado', 'telefono', 'cargo'
            ],
            'opciones_validas': {
                'tipo': [x[0] for x in TIPO_CHOICES],
                'sexo': SEXO_CHOICES,
                'color_piel': COLOR_PIEL_CHOICES,
                'estado_civil': ESTADO_CIVIL_CHOICES,
                'procedencia_social': PROCEDENCIA_SOCIAL_CHOICES,
                'categoria_docente': CATEGORIA_DOCENTE_CHOICES,
                'grado_cientifico': GRADO_CIENTIFICO_CHOICES
            },
            'validaciones_regex': {
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
            'longitudes_maximas': {
                'nombres': 100, 'primer_apellido': 100, 'segundo_apellido': 100,
                'ci': 11, 'lugar_nacimiento': 100, 'ciudadano': 100, 'pais': 100,
                'direccion': 500, 'telefono': 20, 'solapin': 50
            },
            'rangos_numericos': {
                'salario': (1, 999999)  # Mínimo 1, máximo 999,999
            },
            'campos_fecha': ['fecha_otorgamiento_categoria', 'fecha_otorgamiento_grado'],
            'campos_unique': ['ci', 'solapin']
        }

        tipo = datos.get('tipo', '').strip()

        # Validación campos obligatorios generales
        for campo in CONFIG['campos_obligatorios_generales']:
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

        # Validación rangos numéricos
        for campo, (min_val, max_val) in CONFIG['rangos_numericos'].items():
            valor = datos.get(campo)
            if valor:
                try:
                    valor_num = float(valor)
                    if valor_num < min_val:
                        errores.append(f"El campo '{campo}' no puede ser menor que {min_val}")
                    if valor_num > max_val:
                        errores.append(f"El campo '{campo}' no puede ser mayor que {max_val}")
                except (ValueError, TypeError):
                    errores.append(f"El campo '{campo}' debe ser un número válido")

        # Validación de unicidad
        for campo in CONFIG['campos_unique']:
            valor = datos.get(campo)
            if valor:
                qs =Aspirante.objects.filter(**{campo: valor})
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

        # Validaciones específicas por tipo
        if tipo == 'Estudiante':
            # Facultad obligatoria para estudiantes
            if not datos.get('facultad'):
                errores.append("Para estudiantes, el campo 'facultad' es obligatorio")
            
            # Campos que no deben estar presentes para estudiantes
            campos_no_permitidos = [
                'ces', 'departamento', 'categoria_docente', 
                'fecha_otorgamiento_categoria', 'grado_cientifico',
                'fecha_otorgamiento_grado'
            ]
            for campo in campos_no_permitidos:
                if datos.get(campo):
                    errores.append(f"Estudiantes no deben tener valor en '{campo}'")
            
            # Establecer cargo por defecto
            datos['cargo'] = 'Estudiante'

        elif tipo == 'Profesor':
            # Cargo obligatorio para profesores
            if not datos.get('cargo'):
                errores.append("Para profesores, el campo 'cargo' es obligatorio")

            # Validar que categoría docente y fecha vayan juntas
            if bool(datos.get('categoria_docente')) != bool(datos.get('fecha_otorgamiento_categoria')):
                errores.append("La categoría docente y su fecha de otorgamiento deben ir juntas")

            # Validar que grado científico y fecha vayan juntas
            if bool(datos.get('grado_cientifico')) != bool(datos.get('fecha_otorgamiento_grado')):
                errores.append("El grado científico y su fecha de otorgamiento deben ir juntas")

        # Validar que si existe teléfono, sea válido
        if datos.get('telefono'):
            if not re.match(CONFIG['validaciones_regex']['telefono'][0], str(datos['telefono'])):
                errores.append(CONFIG['validaciones_regex']['telefono'][1])

        return 'OK' if not errores else ', '.join(errores) + "."








class RRHH(models.Model):
    userid = models.OneToOneField(User,on_delete=models.CASCADE,null=False)
    
