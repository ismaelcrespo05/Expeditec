from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.Configuracion.as_view(),name='configuracion'),
    path('verificacion_mail/',include('verificacion_email.urls')),
    path('cambiar_clave/',views.Cambiar_clave.as_view(),name="cambiar_clave"),
]
