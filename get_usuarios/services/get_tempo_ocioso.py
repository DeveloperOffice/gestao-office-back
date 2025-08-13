from django.http import JsonResponse
from odbc_reader.services import fetch_data

def get_tempo_ocioso(request):
    query = """
        SELECT
        geconexoesativas.i_conexoesativas,
        geconexoesativas.i_conexao_id,
        geconexoesativas.i_produto,
        geconexoesativas.ocioso_acumulado,
        geconexoesativas.ocioso_acum_seg

        FROM bethadba.geconexoesativas
    """
    data = fetch_data(query)
    return JsonResponse(data, safe=False)
