
from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime, timedelta

def rename_key(list, mapping):
    for item in list:
        for chave_antiga, chave_nova in mapping.items():
            if chave_antiga in item:
                item[chave_nova] = item.pop(chave_antiga)
    return list


def get_cliente():
    try:
        query = 'SELECT * FROM bethadba.HRCLIENTE'
        result = fetch_data(query)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"Clientes": result}, safe=False)

    

def get_empresa():
    try:        
        query = 'SELECT nome_emp, cepe_emp, cgce_emp, ramo_emp, codi_emp, rleg_emp, stat_emp, dina_emp, dcad_emp, ccae_emp, cpf_leg_emp, cnae_emp, codi_con, email_emp, dtinicio_emp, duracao_emp, dttermino_emp, razao_emp, tipoi_emp, i_cnae20, usa_cnae20, email_leg_emp, CERTIFICADO_DIGITAL   FROM bethadba.geempre'
        result = fetch_data(query)
        key_mapping = {
        "nome_emp": "nome_empresa",
        "cepe_emp": "CEP",
        "cgce_emp": "cnpj",
        "ramo_emp": "ramo_atividade",
        "codi_emp": "codigo_empresa",
        "rleg_emp": "responsavel_legal",
        "stat_emp": "situacao",
        "dina_emp": "data_inatividade",
        "dcad_emp": "data_cadastro",
        "ccae_emp": "CAE",
        "cpf_leg_emp": "cpf_responsavel",
        "cnae_emp": "CNAE",
        "codi_con": "contador",
        "email_emp": "email",
        "dtinicio_emp": "data_inicio_atividades",
        "duracao_emp": "duracao_contrato",
        "dttermino_emp": "data_termino_contrato",
        "razao_emp": "razao_social",
        "tipoi_emp": "motivo_inatividade",
        "i_cnae20": "CNAE_20",
        "usa_cnae20": "usa_CNAE_20",
        "email_leg_emp": "email_resp_legal",
        "CERTIFICADO_DIGITAL": "cert_digital",

        
        }
        filtered_result = rename_key(result, key_mapping)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)
    
    return JsonResponse({"Empresas": filtered_result}, safe=False)


def get_imposto():
    hoje = datetime.now()
    mes_atual = hoje.month

    # Definir o ano atual e o próximo ano
    if mes_atual == 1:
        ano_atual = hoje.year - 1
    else:
        ano_atual = hoje.year

    proximo_ano = ano_atual + 1

    # Calcular a data de 5 meses anteriores
    cinco_meses_anteriores = (hoje.replace(year=ano_atual, month=mes_atual) - timedelta(days=150))

    # Montar a query ajustada
    query = f"""
    SELECT codi_emp, codi_imp, data_sim, pdic_sim, sdev_sim, scre_sim
    FROM bethadba.efsdoimp 
    WHERE data_sim >= '{cinco_meses_anteriores.strftime('%Y-%m-%d')}'
    AND data_sim <= '{hoje.strftime('%Y-%m-%d')}'
    """

    # Executar a query
    result = fetch_data(query)
    
    return JsonResponse({"Impostos": result}, safe=False)