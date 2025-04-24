from django.contrib import admin
from django.urls import path
from authenticator.views import get_login

urlpatterns = [
    # Listar
    path("auth", get_login.as_view(), name="autenticar_login"),
]
