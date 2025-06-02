from rest_framework import serializers

class ModuloRequestSerializer(serializers.Serializer):
    api_token = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

class UsuarioSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    atividades = serializers.DictField(child=serializers.IntegerField())
    total_usuario = serializers.IntegerField()

class ModuloSerializer(serializers.Serializer):
    usuarios = UsuarioSerializer(many=True)
    total_sistema = serializers.IntegerField()

class ModuloResponseSerializer(serializers.Serializer):
    __root__ = serializers.DictField(child=ModuloSerializer())
