from django.urls import path
from . import views

urlpatterns = [
    # Rota para chamar a função de calcular
    path('calcular/', views.calcular, name='calcular'),
]
