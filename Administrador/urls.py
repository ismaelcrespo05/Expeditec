from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.Dashboard.as_view(),name='admin_dashboard'),
    path('personal/',views.Personal.as_view(),name='personal'),
    path('nuevo_personal/',views.Nuevo_Personal.as_view(),name='nuevo_personal'),
    path('busqueda/',views.Busqueda_Personal.as_view(),name='busqueda_personal'),
]
