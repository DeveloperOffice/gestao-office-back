from django.http import JsonResponse
from odbc_reader.services import fetch_data
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  
import json
from get_usuarios.services.get_tempo_ocioso import get_tempo_ocioso

class get_tempo_ocioso_view(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)

        data = get_tempo_ocioso(request)
        return JsonResponse({'tempo_ocioso': json.loads(data.content)}, safe=False)
