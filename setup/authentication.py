from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

class BodyTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Tenta obter o token primeiro do corpo (se for JSON) ou dos parâmetros da query
        token_key = (
            request.data.get('api_token') if hasattr(request, 'data') else None
        ) or request.query_params.get('api_token')

        # Caso o token não seja encontrado
        if not token_key:
            return None  # sem token, DRF tenta a próxima classe de autenticação (ou nega)

        # Verifica se o token é válido no banco de dados
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Token inválido.')

        # Retorna o usuário e o token se autenticado
        return (token.user, token)
