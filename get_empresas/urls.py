from django.contrib import admin
from django.urls import path
from get_empresas.views.listar import get_empresas

urlpatterns = [
    path('listar', get_empresas.as_view(), name='listar_empresas'),
 
]
