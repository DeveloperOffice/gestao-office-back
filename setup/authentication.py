from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

class BodyTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token_key = (
            request.data.get('api_token') if hasattr(request, 'data') else None
        ) or request.query_params.get('api_token')

        if not token_key:
            return None  # sem token, DRF tenta a próxima auth class (ou nega)

        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Token inválido.')

        return (token.user, token)
