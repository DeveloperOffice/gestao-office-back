from django.http import JsonResponse
from odbc_reader.services import fetch_data

def get_faturamento(data_inicial, data_final):
    try:
        query = f"""
            SELECT
                efsaidas.codi_emp,
                efsaidas.dsai_sai,
                efsaidas.vcon_sai,
                efsaidas.vexc_sai
                efservicos.vcon_ser
            FROM bethadba.efsaidas,
            bethadba.efservicos
            WHERE efsaidas.codi_emp = efservicos.codi_emp
                AND efsaidas.dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'
        """
        
        result = fetch_data(query)
        if not result:
            return JsonResponse({"message": "Nenhum dado encontrado"},status=404)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(result, safe=False)