from rest_framework import serializers


class MesValueSerializer(serializers.Serializer):
    valor = serializers.CharField(allow_null=True, required=False)
    diferenca = serializers.CharField(allow_null=True, required=False)


class FaturamentoValorSerializer(serializers.DictField):
    child = MesValueSerializer()


class TotalSerializer(serializers.Serializer):
    Total_Saidas = serializers.CharField(source="Total Saidas", allow_null=True, required=False)
    Total_servicos = serializers.CharField(source="Total servicos", allow_null=True, required=False)


class FaturamentoSerializer(serializers.Serializer):
    Saidas = FaturamentoValorSerializer()
    servicos = FaturamentoValorSerializer()
    Total = TotalSerializer()


class EmpresaFaturamentoSerializer(serializers.Serializer):
    codi_emp = serializers.CharField()
    Faturamento = FaturamentoSerializer()


class InfoProcessamentoSerializer(serializers.Serializer):
    total_registros = serializers.IntegerField()
    empresas_encontradas = serializers.IntegerField()
    meses_periodo = serializers.ListField(child=serializers.CharField())


class DadosListField(serializers.ListField):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            try:
                data = [data[str(i)] for i in range(len(data))]
            except KeyError:
                raise serializers.ValidationError("Chaves de 'dados' devem ser números sequenciais como strings.")
        return super().to_internal_value(data)


class FaturamentoResponseSerializer(serializers.Serializer):
    dados = DadosListField(child=EmpresaFaturamentoSerializer(), help_text="Lista de faturamento das empresas")
    info_processamento = InfoProcessamentoSerializer()


class FaturamentoRequestSerializer(serializers.Serializer):
    api_token = serializers.CharField(help_text="Token de autenticação", required=True)
    start_date = serializers.DateField(help_text="Periodo inicial para requisição YYYY/MM/DD", required=True)
    end_date = serializers.DateField(help_text="Periodo final para requisição YYYY/MM/DD", required=True)
