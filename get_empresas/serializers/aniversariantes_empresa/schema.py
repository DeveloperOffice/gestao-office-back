from drf_spectacular.utils import extend_schema, OpenApiExample
from get_empresas.serializers.aniversariantes_empresa.serializer import AniversariosCadastroRequestSerializer, AniversariosCadastroResponseSerializer


ANIVERSARIOS_EMPRESA = {
    "tags": ["Empresa"],
    "summary": "Lista de Empresas Aniversáriantes.",
    "description": "Recebe apenas a api_token e retorna todas as empresas com aniversário de cadastro no mês atual.",
    "request": AniversariosCadastroRequestSerializer,
    "responses": {200: AniversariosCadastroResponseSerializer(many=True)},
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
            value={
                "aniversarios": {
                    "aniversariante_cadastro": {
                        "total": 5,
                        "empresas": [
                            {
                                "codi_emp": 1001,
                                "nome": "TECHNOLOGY INNOVATION LTDA",
                                "cnpj": "12345678000190",
                                "data_cadastro": "2015-07-15",
                                "data_inicio_atividades": "2015-05-10"
                            },
                            {
                                "codi_emp": 1002,
                                "nome": "GREEN SOLUTIONS BRASIL",
                                "cnpj": "98765432000121",
                                "data_cadastro": "2018-07-20",
                                "data_inicio_atividades": "2018-03-15"
                            },
                            {
                                "codi_emp": 1003,
                                "nome": "FUTURE CONSULTING & PARTNERS",
                                "cnpj": "45678912000134",
                                "data_cadastro": "2020-07-01",
                                "data_inicio_atividades": "2020-01-30"
                            },
                            {
                                "codi_emp": 1004,
                                "nome": "URBAN STYLE CONFECÇÕES",
                                "cnpj": "32165498000176",
                                "data_cadastro": "2019-07-10",
                                "data_inicio_atividades": "2019-04-22"
                            },
                            {
                                "codi_emp": 1005,
                                "nome": "NATURAL HEALTH PRODUCTS",
                                "cnpj": "65412378000155",
                                "data_cadastro": "2017-07-05",
                                "data_inicio_atividades": "2017-02-18"
                            }
                        ]
                    }
                }
            },
            response_only=True,
            status_codes=["200"],
        ),
    ],
}