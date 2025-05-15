from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.AspiranteDashboardView.as_view(),name='aspirante_dashboard'),
    path('busqueda/',include('Busqueda_Personal.urls')),
    path('configuracion/',include('Configuracion.urls')),
    path('expediente_docente/',views.ExpedienteDocenteView.as_view(),name="expediente_docente"),
    path('eliminar_documento/',views.Eliminar_ExpedienteDocenteView.as_view(),name="eliminar_documento"),
    path('reemplazar_documento/',views.Update_ExpedienteDocenteView.as_view(),name="reemplazar_documento"),
    path('cambio_categoria/',views.Cambio_Categoria.as_view(),name="cambio_categoria"),
    path('nueva_solicitud/',views.Generar_Solicitud.as_view(),name="nueva_solicitud"),
    path('eliminar_solicitud/',views.Eliminar_Solicitud,name="eliminar_solicitud"),
    path('tribunales/',views.Tribunal.as_view(),name='tribunales'),
    path('aprobar',views.Aprobar_solicitud.as_view(),name="aprobar"),
    path('rechazar/',views.Rechazar_solicitud.as_view(),name="rechazar"),
    path('eliminar_acta/',views.Eliminar_acta_tribunal.as_view(),name="eliminar_acta")
]
