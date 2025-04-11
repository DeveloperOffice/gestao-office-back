from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_importacoes_empresa(start_date, end_date):
    try:
        def agrupar_por_empresa_mes(query_result):
            dados = {}
            for row in query_result:
                codi_emp = row['codi_emp']
                mes = row['mes']
                total = row['total_ocorrencias']

                if codi_emp not in dados:
                    dados[codi_emp] = {i: 0 for i in range(1, 13)}  # meses de 1 a 12

                dados[codi_emp][mes] += total

            return dados

        # Queries
        query_saida = f"""
        SELECT codi_emp, EXTRACT(MONTH FROM dsai_sai) AS mes, COUNT(*) AS total_ocorrencias
        FROM bethadba.efsaidas
        WHERE dsai_sai BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, mes
        ORDER BY codi_emp, mes
        """

        query_entrada = f"""
        SELECT codi_emp, EXTRACT(MONTH FROM dent_ent) AS mes, COUNT(*) AS total_ocorrencias
        FROM bethadba.efentradas
        WHERE dent_ent BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, mes
        ORDER BY codi_emp, mes
        """

        query_servicos = f"""
        SELECT codi_emp, EXTRACT(MONTH FROM dser_ser) AS mes, COUNT(*) AS total_ocorrencias
        FROM bethadba.efservicos
        WHERE dser_ser BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, mes
        ORDER BY codi_emp, mes
        """

        query_lancamentos = f"""
        SELECT codi_emp, EXTRACT(MONTH FROM data_lan) AS mes, COUNT(*) AS total_ocorrencias
        FROM bethadba.ctlancto
        WHERE data_lan BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, mes
        ORDER BY codi_emp, mes
        """

        query_lancamentos_manuais = f"""
        SELECT codi_emp, EXTRACT(MONTH FROM data_lan) AS mes, COUNT(*) AS total_ocorrencias
        FROM bethadba.ctlancto
        WHERE data_lan BETWEEN '{start_date}' AND '{end_date}'
          AND origem_reg != 0
        GROUP BY codi_emp, mes
        ORDER BY codi_emp, mes
        """

        # Executar queries
        result_saida = fetch_data(query_saida)
        result_entrada = fetch_data(query_entrada)
        result_servicos = fetch_data(query_servicos)
        result_lancamentos = fetch_data(query_lancamentos)
        result_lancamentos_manuais = fetch_data(query_lancamentos_manuais)

        # Agrupar os dados
        saidas = agrupar_por_empresa_mes(result_saida)
        entradas = agrupar_por_empresa_mes(result_entrada)
        servicos = agrupar_por_empresa_mes(result_servicos)
        lancamentos = agrupar_por_empresa_mes(result_lancamentos)
        lancamentos_manuais = agrupar_por_empresa_mes(result_lancamentos_manuais)

        # Meses do período
        primeiro_mes = int(datetime.strptime(start_date, '%Y-%m-%d').strftime('%m'))
        ultimo_mes = int(datetime.strptime(end_date, '%Y-%m-%d').strftime('%m'))
        meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

        # Montar resposta
        importacoes = []
        todos_emp = set(
            list(saidas.keys()) +
            list(entradas.keys()) +
            list(servicos.keys()) +
            list(lancamentos.keys()) +
            list(lancamentos_manuais.keys())
        )

        for codi_emp in todos_emp:
            dados_emp = {
                "entradas": {},
                "saidas": {},
                "servicos": {},
                "lancamentos": {},
                "lancamentos_manuais": {},
                "total_entradas": 0,
                "total_saidas": 0,
                "total_servicos": 0,
                "total_lancamentos": 0,
                "total_lancamentos_manuais": 0,
                "total_geral": 0
            }

            for i in range(primeiro_mes, ultimo_mes + 1):
                nome_mes = meses[i - 1]

                entradas_mes = entradas.get(codi_emp, {}).get(i, 0)
                saidas_mes = saidas.get(codi_emp, {}).get(i, 0)
                servicos_mes = servicos.get(codi_emp, {}).get(i, 0)
                lancamentos_mes = lancamentos.get(codi_emp, {}).get(i, 0)
                lancamentos_manuais_mes = lancamentos_manuais.get(codi_emp, {}).get(i, 0)

                dados_emp["entradas"][nome_mes] = entradas_mes
                dados_emp["saidas"][nome_mes] = saidas_mes
                dados_emp["servicos"][nome_mes] = servicos_mes
                dados_emp["lancamentos"][nome_mes] = lancamentos_mes
                dados_emp["lancamentos_manuais"][nome_mes] = lancamentos_manuais_mes

                dados_emp["total_entradas"] += entradas_mes
                dados_emp["total_saidas"] += saidas_mes
                dados_emp["total_servicos"] += servicos_mes
                dados_emp["total_lancamentos"] += lancamentos_mes
                dados_emp["total_lancamentos_manuais"] += lancamentos_manuais_mes

            dados_emp["total_geral"] = (
                dados_emp["total_entradas"] +
                dados_emp["total_saidas"] +
                dados_emp["total_servicos"] +
                dados_emp["total_lancamentos"]
            )

            importacoes.append({
                "codi_emp": codi_emp,
                "importacoes": dados_emp
            })

        return importacoes

    except Exception as e:
        logger.exception("Erro ao calcular importações por empresa.")
        return JsonResponse({"error": str(e)}, status=500)
