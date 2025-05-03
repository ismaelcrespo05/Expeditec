from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.AspiranteDashboardView.as_view(),name='aspirante_dashboard'),
    path('busqueda/',include('Busqueda_Personal.urls')),
    path('configuracion/',include('Configuracion.urls')),
    path('expediente_docente/',views.ExpedienteDocenteView.as_view(),name="expediente_docente")
]
