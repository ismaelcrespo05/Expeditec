from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.Busqueda_Personal.as_view(),name='busqueda_personal'),
    path('expediente/',views.Expedientes_Personal.as_view(),name="expediente_personal"),
    path('aplicar_filtro/',views.Aplicar_filtros.as_view(),name="aplicar_filtro"),
    path('delete_aspirante/',views.Eliminar_personal.as_view(),name="eliminar_personal"),
    path('activar_personal/',views.Activar_personal.as_view(),name='activar_personal'),
]
