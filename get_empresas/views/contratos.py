from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_contratos_data import get_contratos
from get_empresas.serializers.contratos.schema import CONTRATOS_SCHEMA
from get_empresas.serializers.contratos.serializer import (
    ContratosResponseSerializer,
)

from drf_spectacular.utils import extend_schema

@extend_schema(**CONTRATOS_SCHEMA)
class get_contrato(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Chama a função original sem modificações
        result = get_contratos()
        
        # 2. Verifica erro (mantendo sua lógica original)
        if isinstance(result, dict) and "error" in result:
            return JsonResponse(result, status=500)
        
        # 3. Adapta o resultado para o formato esperado
        if not isinstance(result, list):
            result = [result] if result else []
        
        # 4. Cria a resposta estruturada
        response_data = {"Contratos": result}
        
        # 5. Valida o formato de saída (opcional)
        serializer = ContratosResponseSerializer(data=response_data)
        if not serializer.is_valid():
            # Se não validar, retorna o original mesmo assim
            return JsonResponse({"Contratos": result}, safe=False)
            
        return Response(serializer.data)