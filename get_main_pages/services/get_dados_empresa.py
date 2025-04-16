from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def rename_key(list, mapping):
    for item in list:
        for chave_antiga, chave_nova in mapping.items():
            if chave_antiga in item:
                item[chave_nova] = item.pop(chave_antiga)
    return list


def get_empresa():
    try:
        # Query original
        query = """
        SELECT 
            geempre.nome_emp, 
            geempre.cepe_emp, 
            geempre.cgce_emp, 
            geempre.codi_emp,
            HRCLIENTE.CODI_EMP AS escritorio,
            HRCLIENTE.I_CLIENTE AS id_cliente, 
            geempre.rleg_emp, 
            geempre.stat_emp, 
            geempre.dina_emp,
            geempre.dtinicio_emp, 
            geempre.dcad_emp, 
            geempre.cpf_leg_emp, 
            geempre.codi_con, 
            geempre.email_emp 
        FROM bethadba.geempre 
        JOIN bethadba.HRCLIENTE ON geempre.codi_emp = HRCLIENTE.I_CLIENTE_FIXO
        """
        result = fetch_data(query)
        key_mapping = {
            "nome_emp": "nome_empresa",
            "cepe_emp": "CEP",
            "cgce_emp": "cnpj",
            "codi_emp": "codigo_empresa",
            "rleg_emp": "responsavel_legal",
            "stat_emp": "situacao",
            "dina_emp": "data_inatividade",
            "dtinicio_emp": "data_inicio",
            "dcad_emp": "data_cadastro",
            "cpf_leg_emp": "cpf_responsavel",
            "codi_con": "contador",
            "email_emp": "email",
        }

        empresas_raw = rename_key(result, key_mapping)

        # Pegar contratos válidos (sem término ou com término no futuro)
        data_atual = datetime.now().strftime("%Y-%m-%d")
        contratos_query = f"""
            SELECT 
                codi_emp,
                i_cliente,
                VALOR_CONTRATO
            FROM bethadba.HRCONTRATO
            WHERE I_EVENTO = 1 AND (DATA_TERMINO > '{data_atual}' OR DATA_TERMINO IS NULL)
        """
        contratos_result = fetch_data(contratos_query)

        # Criar um índice por (escritorio, id_cliente)
        contratos_map = {}
        for contrato in contratos_result:
            chave = (contrato["codi_emp"], contrato["i_cliente"])
            contratos_map[chave] = contrato["VALOR_CONTRATO"]

        # Agrupar empresas
        empresas = {}
        for item in empresas_raw:
            cod = item["codigo_empresa"]
            escritorio = item["escritorio"]
            id_cliente = item["id_cliente"]
            valor_contrato = contratos_map.get((escritorio, id_cliente))

            if cod not in empresas:
                empresas[cod] = {
                    "codigo_empresa": cod,
                    "nome_empresa": item["nome_empresa"],
                    "CEP": item["CEP"],
                    "cnpj": item["cnpj"],
                    "responsavel_legal": item["responsavel_legal"],
                    "situacao": item["situacao"],
                    "data_inicio": item["data_inicio"],
                    "data_inatividade": item["data_inatividade"],
                    "data_cadastro": item["data_cadastro"],
                    "cpf_responsavel": item["cpf_responsavel"],
                    "contador": item["contador"],
                    "email": item["email"],
                    "escritorios": [],
                }

            empresas[cod]["escritorios"].append(
                {
                    "escritorio": escritorio,
                    "id_cliente": id_cliente,
                    "valor_contrato": valor_contrato,
                }
            )

        return list(empresas.values())

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)
