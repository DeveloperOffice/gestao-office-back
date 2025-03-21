from django.contrib import admin
from django.urls import path
from empresas.views.listar import get_empresas
from empresas.views.clientes import get_clientes
urlpatterns = [
    path('listar/', get_empresas.as_view(), name='listar_empresas'),
    path('clientes/', get_clientes.as_view(), name='listar_clientes')
]
