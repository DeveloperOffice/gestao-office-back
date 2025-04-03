from django.http import JsonResponse
from odbc_reader.services import fetch_data


def get_faturamento():
    try:
        query = 'SELECT * FROM bethadba.HRCLIENTE'
        result = fetch_data(query)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(result, safe=False)