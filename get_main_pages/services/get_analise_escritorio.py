from django.http import JsonResponse
from odbc_reader.services import fetch_data
import logging

logger = logging.getLogger(__name__)

def get_analise_escritorio():
    try:
        query = """
        SELECT DISTINCT
            HRCLIENTE.CODI_EMP AS codigo_escritorio,
            HRCLIENTE.I_CLIENTE_FIXO AS codigo_empresa
        FROM bethadba.HRCLIENTE
        WHERE HRCLIENTE.I_CLIENTE_FIXO IS NOT NULL
        """
        
        result = fetch_data(query)
        
        # Criar dicionário para agrupar empresas por escritório
        escritorios_dict = {}
        
        for item in result:
            codigo_escritorio = item['codigo_escritorio']
            codigo_empresa = item['codigo_empresa']
            
            if codigo_escritorio not in escritorios_dict:
                escritorios_dict[codigo_escritorio] = {
                    'id': codigo_escritorio,
                    'empresas': []
                }
            
            escritorios_dict[codigo_escritorio]['empresas'].append(codigo_empresa)
        
        # Converter o dicionário em lista para retornar
        resultado_final = {
            "escritorios": list(escritorios_dict.values())
        }
        
        return resultado_final

    except Exception as e:
        logger.error(f"Error in get_analise_escritorio: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500, safe=False)