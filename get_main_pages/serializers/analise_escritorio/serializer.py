from rest_framework import serializers


class ImportacoesSerializer(serializers.Serializer):
    entradas = serializers.DictField(child=serializers.IntegerField())
    saidas = serializers.DictField(child=serializers.IntegerField())
    servicos = serializers.DictField(child=serializers.IntegerField())
    lancamentos = serializers.DictField(child=serializers.IntegerField())
    lancamentos_manuais = serializers.DictField(child=serializers.IntegerField())
    porcentagem_lancamentos_manuais = serializers.DictField(
        child=serializers.CharField()
    )
    total_entradas = serializers.IntegerField()
    total_saidas = serializers.IntegerField()
    total_servicos = serializers.IntegerField()
    total_lancamentos = serializers.IntegerField()
    total_lancamentos_manuais = serializers.IntegerField()
    total_geral = serializers.IntegerField()
    porcentagem_total_lancamentos_manuais = serializers.CharField()


class EscritorioSerializer(serializers.Serializer):
    escritorio = serializers.CharField()
    codigo = serializers.IntegerField()
    clientes = serializers.DictField(child=serializers.IntegerField())
    importacoes = ImportacoesSerializer()
    faturamento = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        required=False,
        allow_null=True,
    )
    tempo_ativo = serializers.DictField(child=serializers.IntegerField())
    vinculos_folha_ativos = serializers.DictField(child=serializers.IntegerField())


class RequestSerializer(serializers.Serializer):
    api_token = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class ResponseSerializer(serializers.Serializer):
    __root__ = EscritorioSerializer(many=True)
