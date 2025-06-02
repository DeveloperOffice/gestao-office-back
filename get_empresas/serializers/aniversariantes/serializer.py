from rest_framework import serializers

class AniversariantesRequestSerializer(serializers.Serializer):
    api_token = serializers.CharField(
        help_text="API token gerada pela própria API"
    )

class AniversarianteResponseSerializer(serializers.Serializer):
    socio = serializers.CharField(
        help_text="Nome completo do sócio"
    )
    empresas = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de todas as empresas que o sócio faz parte"
    )
    data_nascimento = serializers.DateField(
        help_text="Data de nascimento do Sócio | YYYY/MM/DD"
    )