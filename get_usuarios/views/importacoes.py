from django.http import JsonResponse
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_usuarios.services.get_importacoes_usuario import get_importacoes
import json

class get_importacao(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
       
    
        result = json.loads(get_importacoes().content)
        return JsonResponse({'Importacoes': result}, safe=False)
    