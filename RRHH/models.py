from django.db import models
from Administrador import models as Admin_models
from Aspirante import models as Aspirante_models
# Create your models here.
CARGOS_CHOICES = ['Presidente','Suplente','Secretario']

class Tribunal(models.Model):
    solicitud_id = models.OneToOneField(Aspirante_models.SolicitudCambioCategoria,on_delete=models.CASCADE,related_name='tribunal')

class Miembro_tribunal(models.Model):
    miembro = models.ForeignKey(Admin_models.Aspirante,on_delete=models.CASCADE,related_name='miembros_tribunales')
    tribunal_id = models.ForeignKey(Tribunal,on_delete=models.CASCADE,related_name='miembros')
    cargo = models.TextField(null=False)
