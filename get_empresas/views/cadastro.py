from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_cadastro import get_aniversariantes
from get_empresas.serializers.aniversariantes_empresa.schema import ANIVERSARIOS_EMPRESA
from get_empresas.serializers.aniversariantes_empresa.serializer import (
    AniversariosCadastroRequestSerializer,
    AniversariosCadastroResponseSerializer
)

from drf_spectacular.utils import extend_schema


@extend_schema(**ANIVERSARIOS_EMPRESA)
class get_cadastro(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1) Valida o request
        req_ser = AniversariosCadastroRequestSerializer(data=request.data)
        req_ser.is_valid(raise_exception=True)

        # 2) Chama o service
        result = get_aniversariantes()

        # 3) Verifica se há erro (mantendo a lógica original)
        if "error" in result:
            return JsonResponse(result, status=500)

        # 4) Serializa a resposta (ajustado para o novo formato)
        resp_ser = AniversariosCadastroResponseSerializer(data=result)
        resp_ser.is_valid(raise_exception=True)
        
        return Response(resp_ser.data)