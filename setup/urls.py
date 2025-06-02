from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from get_api_token.views import CustomObtainAuthToken
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def sucess(request):
    return JsonResponse({"conection": "success"}, status=200)

urlpatterns = [
    path("", sucess),
    path("login/", include("authenticator.urls")),
    path("admin", admin.site.urls),
    path("api/token", CustomObtainAuthToken.as_view(), name="obtain-token"),
    path("empresa/", include("get_empresas.urls")),
    path("folha/", include("get_folha.urls")),
    path("usuarios/", include("get_usuarios.urls")),
    path("main/", include("get_main_pages.urls")),
    # 1) Gera o JSON do esquema OpenAPI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # 2) Swagger UI (interface web interativa)
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # 3) Redoc (outra interface web bonita)
    path(
        "api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
