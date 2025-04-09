from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime


def get_contratos():
    try:
        data_atual = datetime.now().strftime('%Y-%m-%d')
        
        query = f'''
            SELECT 
                codi_emp,
                i_cliente,
                DATA_INICIO,
                DATA_TERMINO,
                VALOR_CONTRATO
            FROM bethadba.HRCONTRATO
            WHERE DATA_TERMINO > '{data_atual}' OR DATA_TERMINO IS NULL
        '''
        result = fetch_data(query)
        return {"Contratos": result}
        
    except Exception as e:
        return {"error": str(e)}