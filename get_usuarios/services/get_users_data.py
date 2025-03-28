from django.http import JsonResponse
from odbc_reader.services import fetch_data

def get_lista_usuario():
    try:
        query = 'SELECT i_usuario, i_confusuario, user_id, usa_modulo_web, usuario_modulo_web, senha_modulo_web, SITUACAO, NOME, USA_ONVIO, LOGIN_ONVIO_VALIDO, USUARIO_ONVIO, SENHA_ONVIO FROM bethadba.usConfUsuario'
        result = fetch_data(query)
        
    except Exception as e:
        
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(result, safe=False)