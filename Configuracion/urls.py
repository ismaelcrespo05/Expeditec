from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.Configuracion.as_view(),name='configuracion'),
]
