from django.http import JsonResponse
from odbc_reader.services import fetch_data
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
def rename_key(list, mapping):
    for item in list:
        for chave_antiga, chave_nova in mapping.items():
            if chave_antiga in item:
                item[chave_nova] = item.pop(chave_antiga)
    return list

class get_contratos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.method != 'GET':
            return JsonResponse({"error": "Método não permitido, use GET"}, status=405)
        
        query = 'SELECT * FROM bethadba.hncontrato'
        result = fetch_data(query)
        key_mapping = {
        "i_contrato": "id_contrato",
        "codi_emp": "codigo_empresa",
        "i_tipocontrato": "id_tipocontrato",
        "i_evento": "id_evento",
        "data_ctr": "data_assinatura",
        "datainicio_ctr": "datainicio_ctr",
        "iniciofat_ctr": "datainicio_faturamento",
        "venctofat_ctr": "mes_vencimento",
        "diavcto_ctr": "dia_faturamento",
        "deftermino_ctr": "definir_datafinal_ctr",
        "datatermino_ctr": "datafinal_ctr",
        "valor_ctr": "valor_ctr",
        "vloriginal_ctr": "valor_original_ctr",
        "nroempr_ctr": "num_empregados",
        "ultrapassarnroempr_ctr": "ultrapassa_num_empregados",
        "ativosmes_ctr": "ativos_mes",
        "demitidosmes_ctr": "demitidos_mes",
        "contribuintes_ctr": "contribuintes",
        "nrolanctos_ctr": "num_lancamentos_contabeis",
        "ultrapassarnrolanctos_ctr": "num_lancamentos_manuais",
        "manualmentectb_ctr": "id_contrato",
        "outromodulosctb_ctr": "id_contrato",
        "importadosctb_ctr": "id_contrato",
        "nronotas_ctr": "id_contrato",
        "ultrapassarnronotas_ctr": "id_contrato",
        "manualmenteefi_ctr": "id_contrato",
        "importadosefi_ctr": "id_contrato",
        "nrohoras_ctr": "id_contrato",
        "ultrapassarnrohoras_ctr": "id_contrato",
        "escrita_ctr": "id_contrato",
        "contabilidade_ctr": "id_contrato",
        "folha_ctr": "id_contrato",
        "patrimonio_ctr": "id_contrato",
        "atualizar_ctr": "id_contrato",
        "lalur_ctr": "id_contrato",
        "registro_ctr": "id_contrato",
        "data_nota_ctr": "id_contrato",
        "data_contab_ctr": "id_contrato"
        
        }
        
        return JsonResponse({"Contratos": result}, safe=False)