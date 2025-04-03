from django.contrib import admin
from django.urls import path
from get_empresas.views.listar import get_empresas
from get_empresas.views.parametros_fiscal import get_contratos
from get_empresas.views.faturamento import get_faturamentos
urlpatterns = [
    path('listar', get_empresas.as_view(), name='listar_empresas'),
    path('contratos', get_contratos.as_view(), name='listar_contratos'),
    path('faturamento', get_faturamentos.as_view(), name='faturamento')
]
