from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from Administrador import models as Admin_models


ESTADOS = ['Pendiente','En revisión','Aprobada','Rechazada']
class SolicitudCambioCategoria(models.Model):
    aspirante = models.ForeignKey(
        Admin_models.Aspirante,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )

    categoria_solicitada = models.TextField(null=False)

    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.TextField(null=False,default='PEN')
    
    # Documentación requerida según Artículo 28 [7][2]
    documentos = models.ManyToManyField('DocumentosExpedienteDocente')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aspirante', 'categoria_solicitada'],
                name='solicitud_unica_por_categoria'
            )
        ]
    
    def __str__(self):
        return f"{self.aspirante} → {self.categoria_solicitada}"






TIPOS_DOCUMENTOS = [
    'Certificación académica',
    'Evaluaciones de desempeño',
    'Aval institucional',
    'Publicaciones científicas',
    'Certificado de idiomas',
    'Examen Problemas Sociales Ciencia/Tecnología'
]

class DocumentosExpedienteDocente(models.Model):
    aspirante_id = models.ForeignKey(
        Admin_models.Aspirante,
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    tipo = models.TextField(null=False)
    archivo = models.FileField(upload_to='soportes/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    valido = models.BooleanField(default=True)
    descripcion = models.TextField(null=False, blank=True)
    def __str__(self):
        return f"{self.tipo} - {self.fecha_subida.date()}"



