from django.contrib import admin
from django.urls import path
from empresas.views import get_empresas
urlpatterns = [
    path('listar/', get_empresas ),
]
