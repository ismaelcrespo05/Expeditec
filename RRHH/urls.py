from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.RRHH_Dashboard.as_view(),name="rrhh_dashboard"),
    path('solicitudes/',views.Solicitudes.as_view(),name="solicitudes"),
]
