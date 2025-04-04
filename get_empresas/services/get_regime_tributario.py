from django.http import JsonResponse
from odbc_reader.services import fetch_data

def get_regime():
    try:        
        query = """SELECT
                EFPARAMETRO_VIGENCIA.CODI_EMP,
                EFPARAMETRO_VIGENCIA.VIGENCIA_PAR,
                EFPARAMETRO_VIGENCIA.RFED_PAR

                FROM bethadba.EFPARAMETRO_VIGENCIA"""
                
        result = fetch_data(query)

  
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)
    
    return result
