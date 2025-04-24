from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.authtoken.views import obtain_auth_token


def sucess(request):
    return JsonResponse({"conection": "success"}, status=200)


urlpatterns = [
    path("", sucess),
    path("login/", include("authenticator.urls")),
    path("admin", admin.site.urls),
    path("api/token", obtain_auth_token),
    path("empresa/", include("get_empresas.urls")),
    path("folha/", include("get_folha.urls")),
    path("usuarios/", include("get_usuarios.urls")),
    path("main/", include("get_main_pages.urls")),
]
