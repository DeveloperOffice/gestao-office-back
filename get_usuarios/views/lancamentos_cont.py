from django.http import JsonResponse
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_usuarios.services.get_lancamentos_cont import get_lancamentos_empresa, get_lancamentos_usuario, get_lancamentos_manuais
import json

class get_lancamento_usuario(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        # Verificação se foram enviadas
        if not start_date or not end_date:
            return JsonResponse({"error": "start_date e end_date são obrigatórios no padrão YYYY-MM-DD"}, status=400)

        # Verificação de formato
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return JsonResponse({"error": "As datas devem estar no formato YYYY-MM-DD"}, status=400)
    
        result = json.loads(get_lancamentos_usuario(start_date, end_date).content)
        return JsonResponse({'Lancamentos': result}, safe=False)


class get_lancamento_empresa(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        # Verificação se foram enviadas
        if not start_date or not end_date:
            return JsonResponse({"error": "start_date e end_date são obrigatórios no padrão YYYY-MM-DD"}, status=400)

        # Verificação de formato
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return JsonResponse({"error": "As datas devem estar no formato YYYY-MM-DD"}, status=400)
    
        result = json.loads(get_lancamentos_empresa(start_date, end_date).content)
        return JsonResponse({'Lancamentos': result}, safe=False)
    
class get_lancamento_manual(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        # Verificação se foram enviadas
        if not start_date or not end_date:
            return JsonResponse({"error": "start_date e end_date são obrigatórios no padrão YYYY-MM-DD"}, status=400)

        # Verificação de formato
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return JsonResponse({"error": "As datas devem estar no formato YYYY-MM-DD"}, status=400)
    
        result = json.loads(get_lancamentos_manuais(start_date, end_date).content)
        return JsonResponse({'Lancamentos': result}, safe=False)
        
        