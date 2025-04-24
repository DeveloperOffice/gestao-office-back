from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from authenticator.services import login_manager


class get_login(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        usuario = str(request.data.get('user'))
        senha = str(request.data.get('password'))
        
        # Verificação se foram enviadas
        if not usuario or not senha:
            return JsonResponse({"error": "start_date e end_date são obrigatórios no padrão YYYY-MM-DD"}, status=400)


        # Tudo certo, chama o service
        result = login_manager(usuario, senha)
        return JsonResponse(result)
    