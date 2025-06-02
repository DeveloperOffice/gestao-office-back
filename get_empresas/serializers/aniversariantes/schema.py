from drf_spectacular.utils import extend_schema, OpenApiExample
from get_main_pages.serializers.analise_cliente.cliente import (
    AnaliseClienteRequestSerializer,
    AnaliseClienteResponseSerializer,
)


ANIVERSARIANTES = {
    "tags":["Empresa"],
    "summary": "Lista de Sócios Aniversáriantes",
    "description": "Recebe apenas a api_token e retorna todos os aniversáriantes do mês atual.",
    "request": AnaliseClienteRequestSerializer,
    "responses": {200: AnaliseClienteResponseSerializer(many=True)},
    "examples": [
        OpenApiExample(
            "Exemplo de Request",
            value={
                "api_token": "79f7db4785845f5fa117dc3a0951241bc50d2d81841be",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Exemplo de Response",
            value=[
                {
                    "socio": "LUCAS DE XEREZ TELESFORO",
                    "empresas": [134],
                    "data_nascimento": "1997-05-27",
                },
                {
                    "socio": "FRANCISCO THIAGO DA SILVA",
                    "empresas": [1, 75, 129, 286, 838, 699, 699, 734, 743, 193, 838],
                    "data_nascimento": "1669-05-28",
                },
                {
                    "socio": "MARIA CARLA MACHADO PEIXOTO",
                    "empresas": [63, 64],
                    "data_nascimento": "1967-05-28",
                },
                {
                    "socio": "MAURICIO PAULO PEREIRA FILHO",
                    "empresas": [669],
                    "data_nascimento": "1969-05-29",
                },
                {
                    "socio": "LARISSA LOIRA PEREIRA",
                    "empresas": [2],
                    "data_nascimento": "2004-05-31",
                },
            ],
            response_only=True,
            status_codes=["200"],
        ),
    ],
}
