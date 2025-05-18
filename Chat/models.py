from django.db import models
from Aspirante import models as Aspirante_models
from django.contrib.auth.models import User
# Create your models here.


class Chat(models.Model):
    solicitud_id = models.OneToOneField(Aspirante_models.SolicitudCambioCategoria,on_delete=models.CASCADE,related_name="chat")



class Miembro_Chat(models.Model):
    chat_id = models.ForeignKey(Chat,on_delete=models.CASCADE,null=False,related_name='miembro_chat')
    userid = models.ForeignKey(User,models.SET_NULL,null=True,related_name="miembro_chat")
    tipo = models.TextField(null=True)



class Mensaje(models.Model):
    contenido = models.TextField(null=False)
    chat_id = models.ForeignKey(Chat,on_delete=models.CASCADE,related_name="mensajes")
    userid = models.ForeignKey(Miembro_Chat,on_delete=models.SET_NULL,null=True,related_name="mensajes")
    timestamp = models.DateTimeField(auto_now_add=True,null=True)
    