from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.Busqueda_Personal.as_view(),name='busqueda_personal'),
]
