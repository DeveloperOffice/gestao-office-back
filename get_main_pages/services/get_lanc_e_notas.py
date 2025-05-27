from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
import calendar
import logging
import json

logger = logging.getLogger(__name__)

MESES_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}
ORDENA_MES_PT = {v: k for k, v in MESES_PT.items()}

def get_importacoes_empresa(start_date, end_date):
    try:
        def agrupar_por_empresa_mes(query_result, data_key):
            dados = {}
            for row in query_result:
                if isinstance(row, bytes):
                    row = json.loads(row.decode("utf-8"))

                codi_emp = row["codi_emp"]
                data = row[data_key]
                mes = data.month
                ano = data.year
                nome_mes = f"{ORDENA_MES_PT[mes]}/{ano}"

                if codi_emp not in dados:
                    dados[codi_emp] = {}

                if nome_mes not in dados[codi_emp]:
                    dados[codi_emp][nome_mes] = 0

                dados[codi_emp][nome_mes] += row["total_ocorrencias"]
            return dados

        # Queries
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

        # Executar e agrupar
        saidas = agrupar_por_empresa_mes(fetch_data(query_saida), "data_ref")
        entradas = agrupar_por_empresa_mes(fetch_data(query_entrada), "data_ref")
        servicos = agrupar_por_empresa_mes(fetch_data(query_servicos), "data_ref")
        lancamentos = agrupar_por_empresa_mes(fetch_data(query_lancamentos), "data_ref")
        lancamentos_manuais = agrupar_por_empresa_mes(fetch_data(query_lancamentos_manuais), "data_ref")

        # Todas empresas
        todos_emp = set(saidas) | set(entradas) | set(servicos) | set(lancamentos) | set(lancamentos_manuais)

        # Todos os meses existentes
        meses_todos = set()
        for fonte in [saidas, entradas, servicos, lancamentos, lancamentos_manuais]:
            for emp in fonte:
                meses_todos.update(fonte[emp].keys())

        # Ordenar os meses corretamente
        meses_ordenados = sorted(
            meses_todos,
            key=lambda x: (int(x.split('/')[1]), MESES_PT[x.split('/')[0]])
        )

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
