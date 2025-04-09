from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_folha.services.get_empregados import get_lista_empregados
import json

class get_empregado(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        result = json.loads(get_lista_empregados().content)
        return JsonResponse({'Dados': result}, safe=False)
        