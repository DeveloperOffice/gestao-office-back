from rest_framework import serializers


class EmpresaSerializer(serializers.Serializer):
    codi_emp = serializers.IntegerField(
        help_text="Código único identificador da empresa"
    )
    nome = serializers.CharField(
        help_text="Nome completo/Razão Social da empresa"
    )
    cnpj = serializers.CharField(
        help_text="CNPJ da empresa (com ou sem formatação)",
        allow_blank=True,
        required=False
    )
    data_cadastro = serializers.DateField(
        help_text="Data de cadastro da empresa no sistema | YYYY-MM-DD",
        required=False,  # Adicionado para tornar o campo opcional
        allow_null=True  # Permite valores nulos
    )
    data_inicio_atividades = serializers.DateField(
        help_text="Data de início das atividades da empresa | YYYY-MM-DD"
    )

class AniversarianteCadastroSerializer(serializers.Serializer):
    total = serializers.IntegerField(
        help_text="Número total de empresas aniversariantes"
    )
    empresas = serializers.ListField(
        child=EmpresaSerializer(),
        help_text="Lista de empresas com aniversário de cadastro"
    )


class AniversariosCadastroResponseSerializer(serializers.Serializer):
    aniversarios = serializers.DictField(
        child=AniversarianteCadastroSerializer(),
        help_text="Dicionário contendo os dados de aniversário de cadastro"
    )


class AniversariosCadastroRequestSerializer(serializers.Serializer):
    api_token = serializers.CharField(
        help_text="API token gerada pela própria API"
    )