from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime, date
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

def get_faturamento(data_inicial, data_final):
    try:
        # Query unificada: saídas + serviços sem correspondência
        query = f"""
            SELECT
                efsaidas.codi_emp,
                efsaidas.dsai_sai AS data,
                efsaidas.vcon_sai AS valor_saida,
                NULL AS valor_servico,
                'saida' AS tipo
            FROM bethadba.efsaidas
            WHERE efsaidas.dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'

            UNION ALL

            SELECT
                efservicos.codi_emp,
                efservicos.dser_ser AS data,
                NULL,
                efservicos.vcon_ser,
                'servico'
            FROM bethadba.efservicos
            WHERE efservicos.dser_ser BETWEEN '{data_inicial}' AND '{data_final}'
              AND NOT EXISTS (
                  SELECT 1 FROM bethadba.efsaidas
                  WHERE efsaidas.codi_emp = efservicos.codi_emp
                    AND efsaidas.dsai_sai = efservicos.dser_ser
              )
        """

        dados = fetch_data(query)
        if not dados:
            return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

        # Mapeamento de meses
        meses = {
            1: "jan", 2: "fev", 3: "mar", 4: "abr",
            5: "mai", 6: "jun", 7: "jul", 8: "ago",
            9: "set", 10: "out", 11: "nov", 12: "dez"
        }

        # Determinar meses no intervalo
        try:
            data_inicial_obj = datetime.strptime(data_inicial, '%Y-%m-%d').date()
            data_final_obj = datetime.strptime(data_final, '%Y-%m-%d').date()

            if data_inicial_obj.year == data_final_obj.year and data_inicial_obj.month == data_final_obj.month:
                meses_periodo = {data_inicial_obj.month: meses[data_inicial_obj.month]}
            elif data_inicial_obj.year == data_final_obj.year:
                meses_periodo = {m: nome for m, nome in meses.items()
                                 if data_inicial_obj.month <= m <= data_final_obj.month}
            else:
                meses_periodo = {m: nome for m, nome in meses.items()
                                 if m >= data_inicial_obj.month or m <= data_final_obj.month}
        except ValueError:
            logger.warning("Erro ao processar datas. Usando todos os meses.")
            meses_periodo = meses

        # Estrutura de resposta
        def criar_estrutura_mensal():
            return {
                "Saidas": {mes: "0" for mes in meses_periodo.values()},
                "servicos": {mes: "0" for mes in meses_periodo.values()},
                "Total": {
                    "Total Saidas": "0",
                    "Total servicos": "0"
                }
            }

        resultado = defaultdict(lambda: {"Faturamento": criar_estrutura_mensal()})
        erros_data = 0
        saidas_processadas = 0
        servicos_processados = 0

        for item in dados:
            codi_emp = str(item.get("codi_emp", ""))
            data = item.get("data")
            tipo = item.get("tipo")

            if not codi_emp or not data:
                continue

            try:
                data_obj = data if isinstance(data, date) else datetime.strptime(data, "%Y-%m-%d").date()
                if data_obj.month not in meses_periodo:
                    continue
                mes = meses_periodo[data_obj.month]
            except Exception as e:
                logger.error(f"Erro ao processar data: {e}")
                erros_data += 1
                continue

            estrutura = resultado[codi_emp]["Faturamento"]

            if tipo == "saida":
                valor = item.get("valor_saida") or 0
                valor_atual = float(estrutura["Saidas"][mes])
                estrutura["Saidas"][mes] = str(valor_atual + float(valor))

                total = float(estrutura["Total"]["Total Saidas"])
                estrutura["Total"]["Total Saidas"] = str(total + float(valor))
                saidas_processadas += 1

            elif tipo == "servico":
                valor = item.get("valor_servico") or 0
                valor_atual = float(estrutura["servicos"][mes])
                estrutura["servicos"][mes] = str(valor_atual + float(valor))

                total = float(estrutura["Total"]["Total servicos"])
                estrutura["Total"]["Total servicos"] = str(total + float(valor))
                servicos_processados += 1

        logger.info(f"Saídas processadas: {saidas_processadas}")
        logger.info(f"Serviços processados: {servicos_processados}")
        logger.info(f"Erros de data: {erros_data}")
        logger.info(f"Empresas encontradas: {len(resultado)}")

        response_data = {
            "dados": resultado,
            "info_processamento": {
                "total_registros": len(dados),
                "saidas_processadas": saidas_processadas,
                "servicos_processados": servicos_processados,
                "erros_data": erros_data,
                "empresas_encontradas": len(resultado),
                "meses_periodo": list(meses_periodo.values())
            }
        }

    except Exception as e:
        logger.exception("Erro ao processar faturamento.")
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(response_data, safe=False)
