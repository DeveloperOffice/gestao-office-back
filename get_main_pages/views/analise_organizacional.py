from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from get_main_pages.services.get_analise_organizacional import get_organizacional


class get_organizacionais(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)

        result = get_organizacional()
        return JsonResponse(result, safe=False, status=200)
