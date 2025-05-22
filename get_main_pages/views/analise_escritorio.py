from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_main_pages.services.get_analise_escritorio import get_analise_escritorio

class get_escritorios(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        result = get_analise_escritorio()
        emp_result = result
        return JsonResponse(emp_result, safe=False)
