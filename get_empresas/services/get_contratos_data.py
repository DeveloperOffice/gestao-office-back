from django.http import JsonResponse
from odbc_reader.services import fetch_data


def get_contratos():
    try:
        query = '''
            SELECT 
                codi_emp,
                i_cliente,
                DATA_INICIO,
                DATA_TERMINO,
                VALOR_CONTRATO
            FROM bethadba.HRCONTRATO
        '''
        result = fetch_data(query)
        return {"Contratos": result}
        
    except Exception as e:
        return {"error": str(e)}