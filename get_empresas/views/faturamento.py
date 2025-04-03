
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_faturamente_empresa import get_faturamento


class get_faturamentos(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        result = get_faturamento()
        return result
