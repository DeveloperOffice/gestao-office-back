from django.http import JsonResponse
from odbc_reader.services import fetch_data


def get_contratos():
    try:
        query = 'SELECT * FROM bethadba.HRCONTRATO'
        result = fetch_data(query)
        return {"Clientes": result}
        
    except Exception as e:
        return {"error": str(e)}