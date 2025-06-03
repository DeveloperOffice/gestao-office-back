from django.contrib import admin
from django.urls import path
from get_main_pages.views.analise_cliente import get_analise_cliente
from get_main_pages.views.analise_usuario import (
    get_analise_usuarios,
    get_analise_usuario_modulo,
)
from get_main_pages.views.analise_escritorio import get_escritorios

from get_main_pages.views.teste import get_teste
from get_main_pages.views.analise_escritorio import get_escritorios
from get_main_pages.views.analise_ficha import get_analise_ficha


urlpatterns = [
    path("cliente", get_analise_cliente.as_view(), name="analise_cliente"),
    path("usuario", get_analise_usuarios.as_view(), name="analise_usuario"),
    path(
        "usuario/modulo",
        get_analise_usuario_modulo.as_view(),
        name="analise_usuario_modulo",
    ),
    path("teste", get_teste.as_view(), name="teste_faturamento"),
    path("ficha", get_analise_ficha.as_view(), name="ficha_pessoal"),
    path("escritorios", get_escritorios.as_view(), name="analise_escritorios"),
]
