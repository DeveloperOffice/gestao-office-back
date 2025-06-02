from drf_spectacular.utils import extend_schema, OpenApiExample
from get_empresas.serializers.contratos.serializer import (
    ContratosRequestSerializer,
    ContratosResponseSerializer,
)

CONTRATOS_SCHEMA = {
    "tags": ["Empresa"],
    "summary": "Lista de Contratos da Empresa",
    "description": "Retorna todos os contratos ativos e inativos de todas as empresas.",
    "request": ContratosRequestSerializer,
    "responses": {200: ContratosResponseSerializer},
    "examples": [
        OpenApiExample(
            "Exemplo de Request",
            value={"api_token": "79f7db4785845f5fa117dc3a0951241bc50d2d81841be"},
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de Response",
            value={
                "Contratos": [
                    {
                        "codi_emp": 75,
                        "i_cliente": 377,
                        "DATA_INICIO": "2020-03-01",
                        "DATA_TERMINO": None,
                        "VALOR_CONTRATO": "541.00",
                    },
                    {
                        "codi_emp": 776,
                        "i_cliente": 40,
                        "DATA_INICIO": "2020-03-01",
                        "DATA_TERMINO": None,
                        "VALOR_CONTRATO": "456.01",
                    },
                    {
                        "codi_emp": 326,
                        "i_cliente": 60,
                        "DATA_INICIO": "2020-03-01",
                        "DATA_TERMINO": "2024-03-01",
                        "VALOR_CONTRATO": "706.01",
                    },
                ]
            },
            response_only=True,
            status_codes=["200"],
        ),
    ],
}
