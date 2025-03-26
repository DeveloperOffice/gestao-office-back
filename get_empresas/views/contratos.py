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
        "ultrapassarnrolanctos_ctr": "ultrapassa_num_lancamentos_contabeis",
        "manualmentectb_ctr": "num_lancamentos_manuais_ctb",
        "outromodulosctb_ctr": "lancamentos_outros_modulos",
        "importadosctb_ctr": "lancamentos_via_txt_ctb",
        "nronotas_ctr": "num_notasfiscais",
        "ultrapassarnronotas_ctr": "ultrapassa_num_notasfiscais",
        "manualmenteefi_ctr": "lancamentos_manualmente_fiscal",
        "importadosefi_ctr": "lancamentos_via_txt_fiscal",
        "nrohoras_ctr": "num_horas_trabalhadas",
        "ultrapassarnrohoras_ctr": "ultrapassa_num_horas_trabalhadas",
        "escrita_ctr": "escrita_fiscal",
        "contabilidade_ctr": "contabilidade",
        "folha_ctr": "folha",
        "patrimonio_ctr": "patrimonio",
        "atualizar_ctr": "atualizar",
        "lalur_ctr": "lalur",
        "registro_ctr": "registro",
        "data_nota_ctr": "data_nota_ctr",
        "data_contab_ctr": "data_contab_ctr"
        }
        
        filtered_result = rename_key(result, key_mapping)
        
        return JsonResponse({"Contratos": filtered_result}, safe=False)