from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.RRHH_Dashboard.as_view(),name="rrhh_dashboard"),
    path('solicitudes/',views.Solicitudes.as_view(),name="solicitudes"),
    path('rechazar_solicitud/',views.Rechazar_Solicitud.as_view(),name="rechazar_solicitud"),
    path('filtrar_solicitudes/',views.filtrar_solicitudes,name='filtrar_solicitudes'),
    path('asignar_tribunal/',views.Asignar_tribunal.as_view(),name="asignar_tribunal"),
    path('eliminar_miembro_tribunal/',views.EliminarMiembroTribunal.as_view(),name="eliminar_miembro_tribunal"),
    path('pasar_a_revision/',views.Pasar_a_revision.as_view(),name="pasar_a_revision"),
    path('exportar_solicitudes/',views.exportar_solicitudes,name="exportar"),
]
