from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('enviar_tocken/', views.Enviar_tocken.as_view(),name='enviar_token'),
]
