from django.contrib import admin
from django.urls import path
from get_folha.views.empregados import get_empregado


urlpatterns = [
    #Listar
    path('empregados', get_empregado.as_view(), name='listar_empregados'),

]
