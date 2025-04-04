from django.http import JsonResponse
from odbc_reader.services import fetch_data

def get_faturamento(data_inicial, data_final):
    try:
        # 1. Saídas com possível serviço (ou NULL se não tiver)
        query_saida = f"""
            SELECT
                efsaidas.codi_emp,
                efsaidas.dsai_sai,
                efsaidas.vcon_sai,
                efsaidas.vexc_sai,
                efservicos.vcon_ser
            FROM bethadba.efsaidas
            LEFT JOIN bethadba.efservicos
              ON efsaidas.codi_emp = efservicos.codi_emp
             AND efsaidas.dsai_sai = efservicos.dser_ser
            WHERE efsaidas.dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'
        """

        # 2. Serviços que não têm nenhuma nota de saída correspondente
        query_servico = f"""
            SELECT
                efservicos.codi_emp,
                efservicos.dser_ser,
                NULL AS vcon_sai,
                NULL AS vexc_sai,
                efservicos.vcon_ser,
                efservicos.cancelada_ser,
                efservicos.codi_acu
            FROM bethadba.efservicos
            WHERE efservicos.dser_ser BETWEEN '{data_inicial}' AND '{data_final}'
              AND NOT EXISTS (
                  SELECT 1
                  FROM bethadba.efsaidas
                  WHERE efsaidas.codi_emp = efservicos.codi_emp
                    AND efsaidas.dsai_sai = efservicos.dser_ser
              )
        """

        dados_saida = fetch_data(query_saida)
        dados_servico = fetch_data(query_servico)

        resultado_completo = (dados_saida or []) + (dados_servico or [])

        if not resultado_completo:
            return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(resultado_completo, safe=False)
