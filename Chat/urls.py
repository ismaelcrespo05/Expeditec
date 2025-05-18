from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('<int:chatid>/',views.Open_Chat.as_view(),name='open_chat'),
]
