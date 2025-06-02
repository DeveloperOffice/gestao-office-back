from drf_spectacular.utils import extend_schema, OpenApiExample
from get_main_pages.serializers.analise_usuario_modulo.serializer import (
    ModuloRequestSerializer,
    ModuloResponseSerializer,
)

MODULOS_SCHEMA = {
    "tags": ["Completos"],
    "summary": "Análise de atividades de usuários por módulo e período",
    "description": "Recebe start_date, end_date e api_token e retorna métricas de atividades por usuário categorizadas por módulo",
    "request": ModuloRequestSerializer,
    "responses": {200: ModuloResponseSerializer},  # classe, não instância
    "examples": [
        OpenApiExample(
            "Exemplo de Request",
            value={
                "start_date": "2025-04-01",
                "end_date": "2025-05-28",
                "api_token": "79f7db4785845fexemplo117dc3exemplo241bc50d2d81841be",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de Response",
            value={
                "Auditoria": {
                    "usuarios": [
                        {
                            "usuario": "GERENTE",
                            "atividades": {"jul/2024": 37},
                            "total_usuario": 37,
                        },
                        {
                            "usuario": "GEISE",
                            "atividades": {"fev/2024": 3, "dez/2024": 124},
                            "total_usuario": 127,
                        },
                    ],
                    "total_sistema": 164,
                },
                "Registro": {
                    "usuarios": [
                        {
                            "usuario": "GERENTE",
                            "atividades": {"jul/2024": 35, "ago/2024": 17},
                            "total_usuario": 52,
                        },
                        {
                            "usuario": "GEISE",
                            "atividades": {"jan/2024": 58},
                            "total_usuario": 58,
                        },
                    ],
                    "total_sistema": 110,
                },
                "Atualizar": {
                    "usuarios": [
                        {
                            "usuario": "NEDISLEI",
                            "atividades": {"jan/2024": 238},
                            "total_usuario": 238,
                        },
                        {
                            "usuario": "GEISE",
                            "atividades": {"set/2024": 8},
                            "total_usuario": 8,
                        },
                        {
                            "usuario": "GABRYEL",
                            "atividades": {"out/2024": 5},
                            "total_usuario": 5,
                        },
                    ],
                    "total_sistema": 251,
                },
            },
            response_only=True,
            status_codes=["200"],  # corrigido para valor único
        ),
    ],
}
