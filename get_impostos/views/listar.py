from django.http import JsonResponse
from odbc_reader.services import fetch_data
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
def rename_key(list, mapping):
    for item in list:
        for chave_antiga, chave_nova in mapping.items():
            if chave_antiga in item:
                item[chave_nova] = item.pop(chave_antiga)
    return list

class get_impostos(APIView):
    permission_classes = [IsAuthenticated]

    
    def post(self, request):
        if request.method != 'POST':
            return JsonResponse({"error": "Método não permitido, use POST"}, status=405)
        
        
        hoje = datetime.now()
        mes_atual = hoje.month

        if mes_atual == 1:
            ano_atual = hoje.year - 1
        else:
            ano_atual = hoje.year

        proximo_ano = ano_atual + 1

        # Query montada com os anos ajustados
        query = f"""
        SELECT codi_emp, codi_imp, data_sim, pdic_sim, sdev_sim, scre_sim
        FROM bethadba.efsdoimp 
        WHERE data_sim = (
            SELECT MAX(data_sim) 
            FROM bethadba.efsdoimp  
            WHERE data_sim >= '{ano_atual}-01-01' 
            AND data_sim < '{proximo_ano}-01-01'
        )
        """

        
        result = fetch_data(query)
        
        return JsonResponse({"Impostos": result}, safe=False)