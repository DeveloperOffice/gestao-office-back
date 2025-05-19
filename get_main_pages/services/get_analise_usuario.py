from django.http import JsonResponse
from odbc_reader.services import fetch_data

import logging


def get_analise_usuario(data_inicial, data_final):
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

        return JsonResponse(result, safe=False)

    except Exception as e:
        logging.exception("Erro na integração dos dados do cliente")
        return JsonResponse({"error": str(e)}, status=500)
