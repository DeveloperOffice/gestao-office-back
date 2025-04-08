from django.http import JsonResponse
from odbc_reader.services import fetch_data
import json
from datetime import datetime


def get_importacoes(start_date, end_date):
    try:
        query = f"""SELECT codi_usu, COUNT(*) AS total_ocorrencias
                    FROM bethadba.efsaidas
                    WHERE dsai_sai BETWEEN '{start_date}' AND '{end_date}'
                    GROUP BY codi_usu
                    ORDER BY total_ocorrencias DESC"""
        result = fetch_data(query)
        
    except Exception as e:
        
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(result, safe=False)








