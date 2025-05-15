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
    observaciones = models.TextField(null=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.TextField(null=False,default='Pendiente')
    fecha_resolucion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.aspirante} → {self.categoria_solicitada}"






TIPOS_DOCUMENTOS = [
    'Certificación académica',
    'Evaluaciones de desempeño',
    'Aval institucional',
    'Publicaciones científicas',
    'Certificado de idiomas',
    'Examen Problemas Sociales Ciencia/Tecnología',
    'Foto de carnet',
    'Tutoría',
    'Otros'
]
def documento_upload_to(instance, filename):
    return f'expedientedocente/{instance.aspirante_id.ci}/{filename}'

class DocumentosExpedienteDocente(models.Model):
    aspirante_id = models.ForeignKey(
        Admin_models.Aspirante,
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    tipo = models.TextField(null=False)
    archivo = models.FileField(upload_to=documento_upload_to)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(null=False, blank=True)
    
    def __str__(self):
        return f"{self.tipo} - {self.fecha_subida.date()}"




# Configuración de autoeliminación de archivos
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=DocumentosExpedienteDocente)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.archivo:
        instance.archivo.delete(save=False)






def actas_upload_to(instance, filename):
    return f'actas_tribunal/{instance.solicitud_id.id}/{filename}'

from RRHH import models as RRHH_models
class Actas_Tribunal(models.Model):
    solicitud_id = models.ForeignKey(SolicitudCambioCategoria,on_delete=models.CASCADE)
    archivo = models.FileField(upload_to=actas_upload_to)
    miembro = models.ForeignKey(RRHH_models.Miembro_tribunal,on_delete=models.SET_NULL,null=True,related_name='actas_tribunal')
    descripcion = models.TextField(null=False, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)



@receiver(post_delete, sender=Actas_Tribunal)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.archivo:
        instance.archivo.delete(save=False)

