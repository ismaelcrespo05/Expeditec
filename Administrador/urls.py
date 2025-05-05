from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.Dashboard.as_view(),name='admin_dashboard'),
    path('personal/',views.Personal.as_view(),name='personal'),
    path('nuevo_personal/',views.Nuevo_Personal.as_view(),name='nuevo_personal'),
    path('busqueda/',include('Busqueda_Personal.urls')),
    path('configuracion/',include('Configuracion.urls')),
    path('registro_personal_csv/',views.Personal_CSV.as_view(),name='personal_csv'),

    path('rrhh/',views.Personal_RRHH.as_view(),name='rrhh'),
    path('delete_rrhh/',views.delete_personal_rrhh,name='delete_personal_rrhh')
]
