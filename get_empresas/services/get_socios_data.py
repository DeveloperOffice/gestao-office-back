from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime


def get_socios():
    try:

        query = f"""
                SELECT
                FOCONTRIBUINTES.CODI_EMP,
                FOCONTRIBUINTES.I_CONTRIBUINTES,
                FOCONTRIBUINTES.NOME,
                FOCONTRIBUINTES.TIPO

                FROM bethadba.FOCONTRIBUINTES
                """
        result = fetch_data(query)
        return {"Contratos": result}

    except Exception as e:
        return {"error": str(e)}
