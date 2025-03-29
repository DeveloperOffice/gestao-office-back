from django.http import JsonResponse
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_usuarios.services.get_users_data import get_atividades_usuario, get_atividades_usuario_cliente
import json

class get_atividades(APIView):
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

        # Tudo certo, chama o service
        result = json.loads(get_atividades_usuario(start_date, end_date).content)
        return JsonResponse({'Atividades': result}, safe=False)
    
class get_atividades_cliente(APIView):
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

        # Tudo certo, chama o service
        result = json.loads(get_atividades_usuario_cliente(start_date, end_date).content)
        return JsonResponse({'Atividades': result}, safe=False)