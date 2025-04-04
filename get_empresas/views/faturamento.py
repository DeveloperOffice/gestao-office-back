
from django.http import JsonResponse
from rest_framework.views import APIView
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.get_faturamente_empresa import get_faturamento
import json


class get_faturamentos(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        start_date = request.data.get ('start_date')
        end_date = request.data.get ('end_date')

        if not start_date or not end_date: 
            return JsonResponse({"error: start_date e end_date são obrigatórios no padrão YYYY-MM-DD"}, status=400)
        
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return JsonResponse({"error": "As datas devem estar no formato YYYY-MM-DD"}, status=400)
        
        result = json.loads(get_faturamento(start_date, end_date).content)
        return JsonResponse (result, safe=False)
            
