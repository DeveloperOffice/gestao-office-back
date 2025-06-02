from rest_framework import serializers

class ContratoSerializer(serializers.Serializer):
    codi_emp = serializers.IntegerField()
    i_cliente = serializers.IntegerField()
    DATA_INICIO = serializers.DateField()
    DATA_TERMINO = serializers.DateField(required=False, allow_null=True)
    VALOR_CONTRATO = serializers.CharField()

class ContratosResponseSerializer(serializers.Serializer):
    Contratos = serializers.ListField(
        child=ContratoSerializer(),
        help_text="Lista de contratos"
    )

class ContratosRequestSerializer(serializers.Serializer):
    api_token = serializers.CharField(
        help_text="Token de autenticação",
        required=False  # Tornando opcional para manter compatibilidade
    )