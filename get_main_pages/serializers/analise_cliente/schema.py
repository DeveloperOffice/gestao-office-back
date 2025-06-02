from drf_spectacular.utils import extend_schema, OpenApiExample
from get_main_pages.serializers.analise_cliente.serializer import (
    AnaliseClienteRequestSerializer,
    AnaliseClienteResponseSerializer,
)

ANALISE_CLIENTE_SCHEMA = {
    "tags":["Completos"],
    "summary": "Análise de atividade de Cliente por período",
    "description": "Recebe start_date, end_date e api_token e retorna métricas por empresa.",
    "request": AnaliseClienteRequestSerializer,
    "responses": {200: AnaliseClienteResponseSerializer(many=True)},
    "examples": [
        OpenApiExample(
            "Exemplo de Request",
            value={
                "start_date": "2025-04-01",
                "end_date": "2025-05-28",
                "api_token": "79f7db4785845f5fa117dc3a0951241bc50d2d81841be",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de Response",
            value=[
                {
                    "codigo_empresa": "9999",
                    "nome_empresa": "EMPRESA EXEMPLO SIMPLES NACIONAL LTDA",
                    "cnpj": "96841580000119",
                    "email": "exemplo.simples@exemplo.com.br",
                    "situacao": "A",
                    "data_cadastro": "2013-01-01",
                    "data_inicio_atv": "2013-01-01",
                    "responsavel": "RESPONSÁVEL LEGAL DA EMPRESA EXEMPLO",
                    "escritorios": [
                        {"escritorio": 75, "id_cliente": 851, "valor_contrato": None},
                        {"escritorio": 638, "id_cliente": 851, "valor_contrato": 1234.80},
                        {"escritorio": 699, "id_cliente": 851, "valor_contrato": None},
                        {"escritorio": 591, "id_cliente": 851, "valor_contrato": 123.34},
                    ],
                    "faturamento": {
                        "jan/2024": [6700.0, "0%"],
                        "fev/2024": [10800.0, "61.19%"],
                    },
                    "importacoes": {
                        "entradas": {"jan/2024": 0, "fev/2024": 2},
                        "saidas": {"jan/2024": 0, "fev/2024": 0},
                        "servicos": {"jan/2024": 2, "fev/2024": 5},
                        "lancamentos": {"jan/2024": 0, "fev/2024": 1},
                        "lancamentos_manuais": {"jan/2024": 0, "fev/2024": 0},
                        "total_entradas": 6,
                        "total_saidas": 0,
                        "total_servicos": 10,
                        "total_lancamentos": 1,
                        "total_lancamentos_manuais": 0,
                        "total_geral": 17,
                    },
                    "empregados": {
                        "jan/2024": 6,
                        "fev/2024": 6,
                        # ...
                    },
                    "atividades": {
                        "total": 5642,
                        "mai/2024": 921,
                        # ...
                    },
                }
            ],
            response_only=True,
            status_codes=["200"],
        ),
    ],
}
