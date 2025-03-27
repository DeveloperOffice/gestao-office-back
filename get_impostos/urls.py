from django.contrib import admin
from django.urls import path
from get_impostos.views.listar import get_impostos

urlpatterns = [
    path('', get_impostos.as_view(), name='listar_impostos'),

]
