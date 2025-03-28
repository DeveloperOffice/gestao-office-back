from django.contrib import admin
from django.urls import path
from get_usuarios.views.lista import get_users


urlpatterns = [
    path('listar', get_users.as_view(), name='listar_usuarios'),
]
