from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from get_folha.services.get_contadores import get_lista_contadores



class get_contador(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)

        result = get_lista_contadores()
        return JsonResponse({"contadores": result}, safe=False)
