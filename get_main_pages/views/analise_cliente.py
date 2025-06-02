# get_main_pages/views/cliente.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from get_main_pages.serializers.analise_cliente.cliente import (
    AnaliseClienteRequestSerializer,
    AnaliseClienteResponseSerializer
)
from get_main_pages.services.get_analise_cliente import get_dados_analise_cliente
from get_main_pages.serializers.analise_cliente.schema import ANALISE_CLIENTE_SCHEMA

@extend_schema(**ANALISE_CLIENTE_SCHEMA)
class get_analise_cliente(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1) Valida o request
        req_ser = AnaliseClienteRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)
        start_date = req_ser.validated_data['start_date']
        end_date = req_ser.validated_data['end_date']
        api_token = req_ser.validated_data['api_token']

        # 2) Chama o service (ajuste a assinatura se precisar usar api_token)
        result = get_dados_analise_cliente(start_date, end_date)

        # 3) Serializa muitos itens de resposta
        resp_ser = AnaliseClienteResponseSerializer(result, many=True)
        return Response(resp_ser.data)
