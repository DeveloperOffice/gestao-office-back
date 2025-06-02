from rest_framework import serializers


class ListaEmpresasRequestSerializer(serializers.Serializer):
    api_token = serializers.CharField(help_text="API token gerada pela própria API")


class EscritorioSerializer(serializers.Serializer):
    codigo_escritorio = serializers.IntegerField()
    id_cliente_contrato = serializers.IntegerField()
    nome_escritorio = serializers.CharField()


class EmpresaSerializer(serializers.Serializer):
    nome_empresa = serializers.CharField(allow_null=True)
    CEP = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    cnpj = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    ramo_atividade = serializers.CharField(allow_null=True)
    CNAE = serializers.FloatField(allow_null=True, required=False)
    CNAE_20 = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    usa_CNAE_20 = serializers.CharField(allow_null=True)
    codigo_empresa = serializers.IntegerField(allow_null=True)
    responsavel_legal = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    situacao = serializers.CharField(allow_null=True)
    data_inatividade = serializers.DateField(allow_null=True, required=False)
    data_cadastro = serializers.DateField(allow_null=True)
    CAE = serializers.FloatField(allow_null=True, required=False)
    cpf_responsavel = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    contador = serializers.IntegerField(allow_null=True, required=False)
    email = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    data_inicio_atividades = serializers.DateField(allow_null=True)
    duracao_contrato = serializers.CharField()
    data_termino_contrato = serializers.DateField(allow_null=True, required=False)
    razao_social = serializers.CharField(allow_null=True)
    motivo_inatividade = serializers.IntegerField(allow_null=True)
    email_resp_legal = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    cert_digital = serializers.CharField(allow_null=True)
    regime_tributario = serializers.CharField(allow_null=True)
    escritorios = EscritorioSerializer(many=True, required=False)

class ListaEmpresasResponseSerializer(serializers.Serializer):
    Empresas = serializers.ListField(child=EmpresaSerializer())
