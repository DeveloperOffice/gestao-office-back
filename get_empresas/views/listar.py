from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_empresas.services.integrate_client_data import integrate_data

class get_empresas(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        result = integrate_data()
        emp_result = result['Empresas']
        return JsonResponse(emp_result, safe=False)
