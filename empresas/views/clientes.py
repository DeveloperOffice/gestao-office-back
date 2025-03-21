from django.http import JsonResponse
from odbc_reader.services import fetch_data


def rename_key(list, mapping):
    for item in list:
        for chave_antiga, chave_nova in mapping.items():
            if chave_antiga in item:
                item[chave_nova] = item.pop(chave_antiga)
    return list
def get_clientes(request):
    if request.method != 'GET':
        return JsonResponse({"error": "Método não permitido, use GET"}, status=405)
    
    query = 'SELECT * FROM bethadba.HRCLIENTE'
    result = fetch_data(query)
    
    return JsonResponse({"Empresas": result}, safe=False)