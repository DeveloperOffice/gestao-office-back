from django.contrib import admin
from django.urls import path
from get_empresas.views.listar import get_empresas
from get_empresas.views.contratos import get_contratos
from get_empresas.views.regime import get_regime_empresas
urlpatterns = [
    path('listar', get_empresas.as_view(), name='listar_empresas'),
    path('contratos', get_contratos.as_view(), name='listar_contratos'),
    path('regime', get_regime_empresas.as_view(), name='listar_Regime'),
]
