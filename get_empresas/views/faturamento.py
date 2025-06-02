from django.http import JsonResponse
from rest_framework.views import APIView
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_faturamento_empresa import get_faturamento
import json
from get_empresas.serializers.faturamento.schema import FATURAMENTO_SCHEMA
from get_empresas.serializers.faturamento.serializer import (
    FaturamentoResponseSerializer,
    FaturamentoRequestSerializer,
)

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response


@extend_schema(**FATURAMENTO_SCHEMA)
class get_faturamentos(APIView):
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

        # 1) Valida o request
        req_ser = FaturamentoRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)

        # 2) Chama o service
        result = json.loads(get_faturamento(start_date, end_date).content)
        # 3) Verifica se há erro (mantendo a lógica original)
        if "error" in result:
            return JsonResponse(result, status=500)

        # 4) Serializa a resposta (ajustado para o novo formato)
        resp_ser = FaturamentoResponseSerializer(data=result)
        resp_ser.is_valid(raise_exception=True)
        return Response(resp_ser.data)
