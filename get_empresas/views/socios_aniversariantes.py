from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_socios_aniversariantes import get_socio_aniversariante
from get_empresas.serializers.aniversariantes.schema import ANIVERSARIANTES
from get_empresas.serializers.aniversariantes.serializer import AniversarianteResponseSerializer, AniversariantesRequestSerializer

from drf_spectacular.utils import extend_schema

@extend_schema(**ANIVERSARIANTES)
class get_aniversariantes(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1) Valida o request
        req_ser = AniversariantesRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)

        # 2) Chama o service (ajuste a assinatura se precisar usar api_token)
        result = get_socio_aniversariante()

        # 3) Serializa muitos itens de resposta
        resp_ser = AniversarianteResponseSerializer(result, many=True)
        return Response(resp_ser.data)
