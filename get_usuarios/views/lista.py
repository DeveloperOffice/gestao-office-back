from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_usuarios.services.get_users_data import get_lista_usuario
import json
class get_users(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        result = json.loads(get_lista_usuario().content)
        return JsonResponse({'usuarios': result}, safe=False)
        