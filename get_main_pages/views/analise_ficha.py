# get_main_pages/views/cliente.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from get_main_pages.serializers.analise_cliente.serializer import (
    AnaliseClienteRequestSerializer,
    AnaliseClienteResponseSerializer
)
from get_main_pages.services.get_analise_ficha import get_cadastros
from get_main_pages.serializers.analise_cliente.schema import ANALISE_CLIENTE_SCHEMA
from datetime import datetime
from django.http import JsonResponse

@extend_schema(**ANALISE_CLIENTE_SCHEMA)
class get_analise_ficha(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)

        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        if not start_date or not end_date:
            return JsonResponse(
                {"error: start_date e end_date são obrigatórios no padrão YYYY-MM-DD"},
                status=400,
            )

        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return JsonResponse(
                {"error": "As datas devem estar no formato YYYY-MM-DD"}, status=400
            )

        result = get_cadastros(start_date, end_date)
        return result
