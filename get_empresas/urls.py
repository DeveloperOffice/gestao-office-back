from django.contrib import admin
from django.urls import path
from get_empresas.views.listar import get_empresas
from get_empresas.views.faturamento import get_faturamentos
from get_empresas.views.contratos import get_contrato
from get_empresas.views.socios import get_socios
from get_empresas.views.ativos import get_ativos

urlpatterns = [
    path('listar', get_empresas.as_view(), name='listar_empresas'),
    path('faturamento', get_faturamentos.as_view(), name='faturamento'),
    path('contrato', get_contrato.as_view(), name='contratos'),
    path('socios', get_socios.as_view(), name='socios'),
    path('ativos', get_ativos.as_view(), name='ativos_mes'),
    
]
