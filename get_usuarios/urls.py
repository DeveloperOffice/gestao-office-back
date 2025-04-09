from django.contrib import admin
from django.urls import path
from get_usuarios.views.lista import get_users
from get_usuarios.views.atividades import get_atividades, get_atividades_cliente, get_atividades_modulo
from get_usuarios.views.importacoes import get_importacao_usuario, get_importacao_empresa
from get_usuarios.views.lancamentos_cont import get_lancamento_empresa, get_lancamento_usuario, get_lancamento_manual

urlpatterns = [
    #Listar
    path('listar', get_users.as_view(), name='listar_usuarios'),
    
    #Atividades
    path('atividades', get_atividades.as_view(), name='atividades_usuarios'),
    path('atividades/cliente', get_atividades_cliente.as_view(), name='atividades_usuarios_cliente'),
    path('atividades/modulo', get_atividades_modulo.as_view(), name='atividades_usuarios_modulo'),
    
    #Importações
    path('importacoes/usuario', get_importacao_usuario.as_view(), name='importacoes_usuarios'),
    path('importacoes/empresa', get_importacao_empresa.as_view(), name='importacoes_empresas'),
    
    #Lançamentos
    path('lancamentos/usuario', get_lancamento_usuario.as_view(), name='lancamentos_usuarios'),
    path('lancamentos/empresa', get_lancamento_empresa.as_view(), name='lancamentos_empresas'),
    path('lancamentos/manual', get_lancamento_manual.as_view(), name='lancamentos_manuais'),
    
]
