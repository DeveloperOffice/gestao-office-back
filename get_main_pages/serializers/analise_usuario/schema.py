from drf_spectacular.utils import extend_schema, OpenApiExample
from get_main_pages.serializers.analise_usuario.serializer import (
    UsuarioRequestSerializer,
    UsuarioResponseSerializer,
)

USUARIOS_SCHEMA = {
    "tags": ["Completos"],
    "summary": "Análise de atividades de usuários por período",
    "description": "Recebe start_date, end_date e api_token e retorna métricas de atividades por usuário",
    "request": UsuarioRequestSerializer,
    "responses": {200: UsuarioResponseSerializer},  # <-- classe, não instância
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
                "analises": [
                    {
                        "usuario_id": "DAISYANE",
                        "nome_usuario": "DAISYANE",
                        "empresas": [
                            {
                                "codi_emp": 2,
                                "atividades": {
                                    "jan/2024": {
                                        "tempo_gasto": 1500,
                                        "importacoes": 10,
                                        "lancamentos": 200,
                                        "lancamentos_manuais": 20,
                                    },
                                    "fev/2024": {
                                        "tempo_gasto": 1300,
                                        "importacoes": 5,
                                        "lancamentos": 180,
                                        "lancamentos_manuais": 15,
                                    },
                                },
                            },
                            {
                                "codi_emp": 16,
                                "atividades": {
                                    "mar/2024": {
                                        "tempo_gasto": 900,
                                        "importacoes": 8,
                                        "lancamentos": 150,
                                        "lancamentos_manuais": 10,
                                    }
                                },
                            },
                        ],
                        "total_entradas": 100,
                        "total_saidas": 50,
                        "total_servicos": 30,
                        "total_lancamentos": 530,
                        "total_lancamentos_manuais": 45,
                        "total_tempo_gasto": 4000,
                        "total_importacoes": 23,
                        "total_geral": 628,
                    },
                    {
                        "usuario_id": "ANTONIA",
                        "nome_usuario": "ANTONIA",
                        "empresas": [
                            {
                                "codi_emp": 3,
                                "atividades": {
                                    "jan/2024": {
                                        "tempo_gasto": 1200,
                                        "importacoes": 12,
                                        "lancamentos": 250,
                                        "lancamentos_manuais": 25,
                                    }
                                },
                            }
                        ],
                        "total_entradas": 80,
                        "total_saidas": 40,
                        "total_servicos": 20,
                        "total_lancamentos": 250,
                        "total_lancamentos_manuais": 25,
                        "total_tempo_gasto": 1200,
                        "total_importacoes": 12,
                        "total_geral": 377,
                    },
                ],
                "totais_gerais": {
                    "total_entradas": 180,
                    "total_saidas": 90,
                    "total_servicos": 50,
                    "total_lancamentos": 780,
                    "total_lancamentos_manuais": 70,
                    "total_tempo_gasto": 5200,
                    "total_importacoes": 35,
                    "total_geral": 1005,
                },
            },
            response_only=True,
            status_codes=["200"],  # string ou int único, não lista
        ),
    ],
}
