from django.http import JsonResponse
from odbc_reader.services import fetch_data

def get_lista_usuario():
    try:
        query = 'SELECT * FROM bethadba.usConfUsuario'
        result = fetch_data(query)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"Clientes": result}, safe=False)