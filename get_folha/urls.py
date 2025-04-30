from django.contrib import admin
from django.urls import path
from get_folha.views.empregados import get_empregado
from get_folha.views.contadores import get_contador

urlpatterns = [
    # Listar
    path("empregados", get_empregado.as_view(), name="listar_empregados"),
    path("contadores", get_contador.as_view(), name="listar_contadores"),
]
