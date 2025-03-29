from django.contrib import admin
from django.urls import path
from get_usuarios.views.lista import get_users
from get_usuarios.views.atividades import get_atividades, get_atividades_cliente


urlpatterns = [
    path('listar', get_users.as_view(), name='listar_usuarios'),
    path('atividades', get_atividades.as_view(), name='atividades_usuarios'),
    path('atividades/clientes', get_atividades_cliente.as_view(), name='atividades_usuarios_cliente'),
]
