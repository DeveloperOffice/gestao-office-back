from rest_framework.authtoken.views import ObtainAuthToken as BaseObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField(
        source="user.id", read_only=True
    )  # Exemplo de campo adicional


class CustomObtainAuthToken(BaseObtainAuthToken):
    serializer_class = AuthTokenSerializer

    @extend_schema(
        tags=["Autenticação"],
        summary="Obter token de acesso",
        description="Autentica usuário e retorna token para APIs protegidas",
        request=AuthTokenSerializer,
        responses={
            200: TokenResponseSerializer,
            400: OpenApiResponse(description="Credenciais inválidas"),
        },
        examples=[
            OpenApiExample(
                "Exemplo válido",
                value={"username": "admin", "password": "senha123"},
                request_only=True,
            ),
            OpenApiExample(
                "Resposta de sucesso",
                value={"token": "a5b578f7f15baa62f3124213c73f94hc6791603d4a61"},
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # Você pode adicionar lógica adicional aqui se necessário
        return response
