from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_socios_data import get_socio


class get_socios(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)

        codigo_empresa = request.data.get("codi_emp")
        
        if not codigo_empresa:
            return JsonResponse({"error": "'codi_emp' é obrigatório."}, safe=False)
        codigo_empresa = int(codigo_empresa)
        result = get_socio(codigo_empresa)

        if "error" in result:
            return JsonResponse(result, status=500)

        return JsonResponse(result, safe=False)
