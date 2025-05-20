from django.http import JsonResponse
from odbc_reader.services import fetch_data


def get_atividades_usuario_total(start_date, end_date):
    try:
        query = f"""
        SELECT * FROM bethadba.geloguser 
        WHERE data_log BETWEEN '{start_date}' AND '{end_date}'
        """
        result = fetch_data(query)

        lenght = len(result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"atividades_totais": lenght}, safe=False)
