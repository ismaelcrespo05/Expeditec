from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.Login.as_view(),name='login'),
    path('logout/',views.Logout.as_view(),name='logout'),
    path('recuperar_clave/',views.Cambio_clave.as_view(),name='recuperar_clave')
]
