from django.contrib import admin
from django.urls import path
from get_main_pages.views.analise_cliente import get_analise_cliente
from get_main_pages.views.analise_usuario import get_analise_usuarios


urlpatterns = [
    path("cliente", get_analise_cliente.as_view(), name="analise_cliente"),
    path("usuario", get_analise_usuarios.as_view(), name="analise_cliente"),
]
