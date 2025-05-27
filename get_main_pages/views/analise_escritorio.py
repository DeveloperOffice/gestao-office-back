from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_main_pages.services.get_analise_escritorio import get_analise_escritorio
import logging

logger = logging.getLogger(__name__)

class get_escritorios(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if request.method != 'POST':
                return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
            
            # Obtém as datas do body da requisição
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')

            # Valida se as datas foram fornecidas
            if not start_date or not end_date:
                return JsonResponse({
                    "error": "As datas inicial e final são obrigatórias",
                    "exemplo": {
                        "start_date": "2024-01-01",
                        "end_date": "2024-03-31"
                    }
                }, status=400)
            
            result = get_analise_escritorio(start_date, end_date)
            return JsonResponse(result, safe=False)

        except Exception as e:
            logger.error(f"Erro ao processar requisição: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
