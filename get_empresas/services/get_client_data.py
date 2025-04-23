from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
from get_empresas.services.categorizacao_cnae import corrigir_categoria_empresa

def rename_key(list, mapping):
    for item in list:
        for chave_antiga, chave_nova in mapping.items():
            if chave_antiga in item:
                item[chave_nova] = item.pop(chave_antiga)
    return list


def get_cliente():
    try:
        query = "SELECT * FROM bethadba.HRCLIENTE"
        result = fetch_data(query)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"Clientes": result}, safe=False)


def get_nome_empresa():
    try:
        query = "SELECT nome_emp, codi_emp, cgce_emp AS cnpj FROM bethadba.geempre"
        result = fetch_data(query)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)

    return result


def get_empresa():
    try:
        query = """
            SELECT nome_emp, cepe_emp, cgce_emp, ramo_emp, codi_emp, rleg_emp, stat_emp, 
                   dina_emp, dcad_emp, ccae_emp, cpf_leg_emp, cnae_emp, codi_con, email_emp, 
                   dtinicio_emp, duracao_emp, dttermino_emp, razao_emp, tipoi_emp, i_cnae20, 
                   usa_cnae20, email_leg_emp, CERTIFICADO_DIGITAL
            FROM bethadba.geempre
        """
        result = fetch_data(query)
        key_mapping = {
            "nome_emp": "nome_empresa",
            "cepe_emp": "CEP",
            "cgce_emp": "cnpj",
            "ramo_emp": "ramo_atividade",
            "cnae_emp": "CNAE",
            "i_cnae20": "CNAE_20",
            "usa_cnae20": "usa_CNAE_20",
            "codi_emp": "codigo_empresa",
            "rleg_emp": "responsavel_legal",
            "stat_emp": "situacao",
            "dina_emp": "data_inatividade",
            "dcad_emp": "data_cadastro",
            "ccae_emp": "CAE",
            "cpf_leg_emp": "cpf_responsavel",
            "codi_con": "contador",
            "email_emp": "email",
            "dtinicio_emp": "data_inicio_atividades",
            "duracao_emp": "duracao_contrato",
            "dttermino_emp": "data_termino_contrato",
            "razao_emp": "razao_social",
            "tipoi_emp": "motivo_inatividade",
            "email_leg_emp": "email_resp_legal",
            "CERTIFICADO_DIGITAL": "cert_digital",
        }

        filtered_result = rename_key(result, key_mapping)
        
        #Categorizar ramo de atividade com a função do arquivo categorizacao_cnae 
        empresas_com_categoria = corrigir_categoria_empresa(filtered_result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)

    return JsonResponse({"Empresas": empresas_com_categoria}, safe=False)
