from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_cadastro import get_aniversariantes


class get_cadastro(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = get_aniversariantes()

        if "error" in result:
            return JsonResponse(result, status=500)

        return JsonResponse(result, safe=False)
