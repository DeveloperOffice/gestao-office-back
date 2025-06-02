from django.http import JsonResponse
from rest_framework.views import APIView
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from get_main_pages.services.get_analise_usuario import (
    get_analise_usuario,
    get_analise_por_sistema,
)
from drf_spectacular.utils import extend_schema
from get_main_pages.serializers.analise_usuario.schema import USUARIOS_SCHEMA
from get_main_pages.serializers.analise_usuario_modulo.schema import MODULOS_SCHEMA

@extend_schema(**USUARIOS_SCHEMA)
class get_analise_usuarios(APIView):
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

        result = get_analise_usuario(start_date, end_date)
        return result

@extend_schema(**MODULOS_SCHEMA)
class get_analise_usuario_modulo(APIView):
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

        result = get_analise_por_sistema(start_date, end_date)
        return result
