from django.contrib import admin
from django.urls import path
from get_usuarios.views.lista import get_users
from get_usuarios.views.atividades import get_atividades, get_atividades_cliente, get_atividades_modulo


urlpatterns = [
    path('listar', get_users.as_view(), name='listar_usuarios'),
    path('atividades', get_atividades.as_view(), name='atividades_usuarios'),
    path('atividades/cliente', get_atividades_cliente.as_view(), name='atividades_usuarios_cliente'),
    path('atividades/modulo', get_atividades_modulo.as_view(), name='atividades_usuarios_modulo'),
]
