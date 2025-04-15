from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_contratos_data import get_contratos

class get_socios(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        result = get_contratos()
        
        if "error" in result:
            return JsonResponse(result, status=500)
            
        return JsonResponse(result, safe=False)