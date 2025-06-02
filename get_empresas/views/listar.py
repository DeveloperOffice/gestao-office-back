from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.integrate_client_data import integrate_data
from drf_spectacular.utils import extend_schema
from get_empresas.serializers.lista_empresas.schema import EMPRESAS_SCHEMA
from get_empresas.serializers.lista_empresas.serializer import (
    ListaEmpresasRequestSerializer,
    ListaEmpresasResponseSerializer
)
from rest_framework.response import Response

@extend_schema(**EMPRESAS_SCHEMA)
class get_empresas(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1) Valida o request
        req_ser = ListaEmpresasRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)

        # 2) Chama o service
        result = integrate_data()

        # 3) Verifica se há erro (mantendo a lógica original)
        if "error" in result:
            return JsonResponse(result, status=500)

        # 4) Serializa a resposta (ajustado para o novo formato)
        resp_ser = ListaEmpresasResponseSerializer(data=result)
        resp_ser.is_valid(raise_exception=True)
        
        return Response(resp_ser.data)




