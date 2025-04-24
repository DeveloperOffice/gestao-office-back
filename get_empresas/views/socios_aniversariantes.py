from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_socios_aniversariantes import get_socio_aniversariante

class get_aniversariantes(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        result = get_socio_aniversariante()

        if "error" in result:
            return JsonResponse(result, status=500)
        
        # Como result é uma lista, usamos safe=False e status 200
        return JsonResponse(result, safe=False, status=200)