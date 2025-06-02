from rest_framework import serializers


class UsuarioRequestSerializer(serializers.Serializer):
    api_token = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class AtividadesSerializer(serializers.Serializer):
    tempo_gasto = serializers.IntegerField()
    importacoes = serializers.IntegerField()
    lancamentos = serializers.IntegerField()
    lancamentos_manuais = serializers.IntegerField()


class EmpresaSerializer(serializers.Serializer):
    codi_emp = serializers.IntegerField()
    atividades = serializers.DictField(
        child=AtividadesSerializer()
    )


class AnaliseSerializer(serializers.Serializer):
    usuario_id = serializers.CharField()
    nome_usuario = serializers.CharField()
    empresas = EmpresaSerializer(many=True)
    
    total_entradas = serializers.IntegerField()
    total_saidas = serializers.IntegerField()
    total_servicos = serializers.IntegerField()
    total_lancamentos = serializers.IntegerField()
    total_lancamentos_manuais = serializers.IntegerField()
    total_tempo_gasto = serializers.IntegerField()
    total_importacoes = serializers.IntegerField()
    total_geral = serializers.IntegerField()


class TotaisGeraisSerializer(serializers.Serializer):
    total_entradas = serializers.IntegerField()
    total_saidas = serializers.IntegerField()
    total_servicos = serializers.IntegerField()
    total_lancamentos = serializers.IntegerField()
    total_lancamentos_manuais = serializers.IntegerField()
    total_tempo_gasto = serializers.IntegerField()
    total_importacoes = serializers.IntegerField()
    total_geral = serializers.IntegerField()


class UsuarioResponseSerializer(serializers.Serializer):
    analises = AnaliseSerializer(many=True)
    totais_gerais = TotaisGeraisSerializer()
