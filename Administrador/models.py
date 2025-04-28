from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
TIPO_CHOICES = ['Profesor','Estudiante']
SEXO_CHOICES = ['Masculino','Femenino']
COLOR_PIEL_CHOICES = ['Blanca','Negra','Mestiza','Asiática']
ESTADO_CIVIL_CHOICES = ['Soltero/a','Casado/a','Divorciado/a','Viudo/a']
PROCEDENCIA_SOCIAL_CHOICES = ['Obrera','Campesina','Intelectual','Otra']
CATEGORIA_DOCENTE_CHOICES = ['Ninguna','ATD Medio Superior','ATD Superior','Instructor','Asistente','Auxiliar','Titular']
GRADO_CIENTIFICO_CHOICES = ['Licenciado','Ingeniero','Máster','Doctor','Ninguno']

class Aspirante(models.Model):
    userid = models.OneToOneField(User,on_delete=models.CASCADE,null=False)
    # Campos principales
    tipo = models.CharField(
        max_length=10,
        verbose_name='Tipo de aspirante'
    )
    
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    primer_apellido = models.CharField(max_length=100, verbose_name='Primer apellido')
    segundo_apellido = models.CharField(
        max_length=100, 
        verbose_name='Segundo apellido', 
        blank=True, 
        null=True
    )
    sexo = models.CharField(
        max_length=1, 
        verbose_name='Sexo'
    )
    ci = models.CharField(
        max_length=11, 
        unique=True, 
        verbose_name='Carné de identidad'
    )
    lugar_nacimiento = models.CharField(
        max_length=100, 
        verbose_name='Lugar de nacimiento'
    )
    color_piel = models.CharField(
        max_length=10,
        verbose_name='Color de piel'
    )
    estado_civil = models.CharField(
        max_length=10, 
        verbose_name='Estado civil'
    )
    ciudadano = models.CharField(
        max_length=100, 
        verbose_name='Ciudadano',
        help_text="Solo se permiten letras y espacios"
    )
    procedencia_social = models.CharField(
        max_length=15, 
        verbose_name='Procedencia social'
    )
    especialidad = models.CharField(
        max_length=100, 
        verbose_name='Especialidad'
    )
    pais = models.CharField(
        max_length=100, 
        verbose_name='País',
        help_text="Solo se permiten letras y espacios"
    )
    centro = models.CharField(
        max_length=100, 
        verbose_name='Centro de trabajo/estudio'
    )
    cargo = models.CharField(
        max_length=100, 
        verbose_name='Cargo'
    )
    facultad = models.CharField(
        max_length=100, 
        verbose_name='Facultad'
    )
    ces = models.CharField(
        max_length=100, 
        verbose_name='CES'
    )
    departamento = models.CharField(
        max_length=100, 
        verbose_name='Departamento'
    )
    salario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name='Salario'
    )
    categoria_docente = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        verbose_name='Categoría docente'
    )
    fecha_otorgamiento_categoria = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Fecha de otorgamiento de categoría'
    )
    direccion = models.TextField(
        max_length=500,
        verbose_name='Dirección particular'
    )
    grado_cientifico = models.CharField(
        max_length=10, 
        blank=True,
        null=True,
        verbose_name='Grado científico'
    )
    fecha_otorgamiento_grado = models.DateField(
        blank=True, 
        null=True,
        verbose_name='Fecha de otorgamiento de grado científico'
    )
    telefono = models.CharField(
        max_length=20, 
        verbose_name='Teléfono'
    )
    solapin = models.CharField(
        max_length=50, 
        verbose_name='Solapín'
    )
    class Meta:
        verbose_name = 'Aspirante'
        verbose_name_plural = 'Aspirantes'
        ordering = ['nombres', 'primer_apellido']
    
    def __str__(self):
        return f"{self.primer_apellido} {self.segundo_apellido or ''}, {self.nombres} ({self.get_tipo_display()})"