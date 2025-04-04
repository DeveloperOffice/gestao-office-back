from django.http import JsonResponse
from odbc_reader.services import fetch_data
import json
from datetime import datetime


def get_importacoes():
    try:
        query = "SELECT * FROM bethadba.fopppatividades"
        result = fetch_data(query)
        
    except Exception as e:
        
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(result, safe=False)








