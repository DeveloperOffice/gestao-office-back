from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
import logging
import calendar

logger = logging.getLogger(__name__)

def get_importacoes_empresa(start_date, end_date):
    try:
        def agrupar_por_empresa_mes(query_result, data_key):
            dados = {}
            for row in query_result:
                codi_emp = row['codi_emp']
                data = row[data_key]
                mes = data.month
                ano = data.year
                chave = f"{calendar.month_abbr[mes].lower()}/{ano}"

                if codi_emp not in dados:
                    dados[codi_emp] = {}

                if chave not in dados[codi_emp]:
                    dados[codi_emp][chave] = 0

                dados[codi_emp][chave] += row['total_ocorrencias']
            return dados

        # Queries com alias do campo de data original
        query_saida = f"""
        SELECT codi_emp, dsai_sai AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.efsaidas
        WHERE dsai_sai BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, dsai_sai
        """

        query_entrada = f"""
        SELECT codi_emp, dent_ent AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.efentradas
        WHERE dent_ent BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, dent_ent
        """

        query_servicos = f"""
        SELECT codi_emp, dser_ser AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.efservicos
        WHERE dser_ser BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, dser_ser
        """

        query_lancamentos = f"""
        SELECT codi_emp, data_lan AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.ctlancto
        WHERE data_lan BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, data_lan
        """

        query_lancamentos_manuais = f"""
        SELECT codi_emp, data_lan AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.ctlancto
        WHERE data_lan BETWEEN '{start_date}' AND '{end_date}'
          AND origem_reg != 0
        GROUP BY codi_emp, data_lan
        """

        # Executar as queries
        result_saida = fetch_data(query_saida)
        result_entrada = fetch_data(query_entrada)
        result_servico = fetch_data(query_servicos)
        result_lancamento = fetch_data(query_lancamentos)
        result_lancamento_manual = fetch_data(query_lancamentos_manuais)

        # Agrupar os resultados por empresa e mês/ano
        saidas = agrupar_por_empresa_mes(result_saida, "data_ref")
        entradas = agrupar_por_empresa_mes(result_entrada, "data_ref")
        servicos = agrupar_por_empresa_mes(result_servico, "data_ref")
        lancamentos = agrupar_por_empresa_mes(result_lancamento, "data_ref")
        lancamentos_manuais = agrupar_por_empresa_mes(result_lancamento_manual, "data_ref")

        # Coletar todos os meses/anos únicos e todas as empresas
        todos_emp = set(
            list(saidas.keys()) +
            list(entradas.keys()) +
            list(servicos.keys()) +
            list(lancamentos.keys()) +
            list(lancamentos_manuais.keys())
        )

        meses_todos = set()
        for fonte in [saidas, entradas, servicos, lancamentos, lancamentos_manuais]:
            for emp in fonte:
                meses_todos.update(fonte[emp].keys())
        meses_ordenados = sorted(meses_todos, key=lambda x: (int(x.split('/')[1]), list(calendar.month_abbr).index(x.split('/')[0].capitalize())))

        # Montar estrutura final
        importacoes = []
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

            for mes in meses_ordenados:
                dados_emp["entradas"][mes] = entradas.get(codi_emp, {}).get(mes, 0)
                dados_emp["saidas"][mes] = saidas.get(codi_emp, {}).get(mes, 0)
                dados_emp["servicos"][mes] = servicos.get(codi_emp, {}).get(mes, 0)
                dados_emp["lancamentos"][mes] = lancamentos.get(codi_emp, {}).get(mes, 0)
                dados_emp["lancamentos_manuais"][mes] = lancamentos_manuais.get(codi_emp, {}).get(mes, 0)

                dados_emp["total_entradas"] += dados_emp["entradas"][mes]
                dados_emp["total_saidas"] += dados_emp["saidas"][mes]
                dados_emp["total_servicos"] += dados_emp["servicos"][mes]
                dados_emp["total_lancamentos"] += dados_emp["lancamentos"][mes]
                dados_emp["total_lancamentos_manuais"] += dados_emp["lancamentos_manuais"][mes]

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
