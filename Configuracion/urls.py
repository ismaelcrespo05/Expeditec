from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.Configuracion.as_view(),name='configuracion'),
    path('verificacion_mail/',include('verificacion_email.urls')),
    path('cambiar_clave/',views.Cambiar_clave.as_view(),name="cambiar_clave"),
    path('cerrar_todas_las_sesiones/',views.cerrar_todas_las_sesiones,name="cerrar_todas_las_sesiones"),
    path('cerrar_sesion_remota',views.cerrar_sesion_remota,name="cerrar_sesion_remota")
]
