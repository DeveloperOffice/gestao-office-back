from django.http import JsonResponse
from odbc_reader.services import fetch_data
import logging
from datetime import datetime, timedelta, date
import json
from get_main_pages.services.get_faturamento import get_faturamento
logger = logging.getLogger(__name__)

# Mês abreviado → número
MESES_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}

# Número → mês abreviado
MESES_NUM_TO_STR = {v: k for k, v in MESES_PT.items()}


def esta_dentro_intervalo(mes_ano: str, start_date, end_date) -> bool:
    try:
        mes_abrev, ano_str = mes_ano.lower().split('/')
        mes = MESES_PT.get(mes_abrev)
        if mes is None:
            logger.error(f"Mes inválido recebido: {mes_abrev}")
            return False
        ano = int(ano_str)

        inicio_mes = datetime(ano, mes, 1)
        fim_mes = (datetime(ano + 1, 1, 1) - timedelta(days=1)) if mes == 12 else (datetime(ano, mes + 1, 1) - timedelta(days=1))

        # Se qualquer data for None, retorna False imediatamente
        if start_date is None or end_date is None:
            logger.error(f"Datas None detectadas: start_date={start_date}, end_date={end_date}")
            return False

        # Tratar start_date
        if isinstance(start_date, str):
            if start_date.lower() == 'nada':
                return False
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        elif isinstance(start_date, date) and not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())

        # Tratar end_date
        if isinstance(end_date, str):
            if end_date.lower() == 'nada':
                return fim_mes >= start_date
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        elif isinstance(end_date, date) and not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.min.time())

        # Finalmente, verifica se inicio_mes <= end_date e fim_mes >= start_date
        if inicio_mes is None or end_date is None or fim_mes is None or start_date is None:
            logger.error("Variável None inesperada nas datas finais")
            return False

        return inicio_mes <= end_date and fim_mes >= start_date

    except Exception as e:
        logger.error(f"Erro em esta_dentro_intervalo: {str(e)}")
        return False

def gerar_meses_em_portugues(start_date: str, end_date: str):
    try:
        data_inicio = datetime.strptime(start_date, "%Y-%m-%d")
        data_fim = datetime.strptime(end_date, "%Y-%m-%d")
        atual = data_inicio.replace(day=1)

        meses_formatados = []
        while atual <= data_fim:
            mes_ano = f"{MESES_NUM_TO_STR[atual.month]}/{atual.year}"
            meses_formatados.append(mes_ano)

            if atual.month == 12:
                atual = atual.replace(year=atual.year + 1, month=1)
            else:
                atual = atual.replace(month=atual.month + 1)

        return meses_formatados

    except Exception as e:
        return {"erro": f"Erro ao gerar meses: {str(e)}"}

def agrupar_por_empresa_mes(query_result, data_key):
    dados = {}
    for row in query_result:
        if isinstance(row, bytes):
            row = json.loads(row.decode("utf-8"))

        codi_emp = row["codi_emp"]
        data = row[data_key]
        mes = data.month
        ano = data.year
        nome_mes = f"{MESES_NUM_TO_STR[mes]}/{ano}"

        if codi_emp not in dados:
            dados[codi_emp] = {}

        if nome_mes not in dados[codi_emp]:
            dados[codi_emp][nome_mes] = 0

        dados[codi_emp][nome_mes] += row["total_ocorrencias"]
    return dados

def get_analise_escritorio(start_date, end_date):
    try:
        # Buscar escritórios
        query_escritorios = """
            SELECT DISTINCT
                geempre.nome_emp AS nome,
                HRCLIENTE.CODI_EMP AS codigo_escritorio,
                HRCLIENTE.I_CLIENTE_FIXO AS codigo_empresa
            FROM bethadba.HRCLIENTE
            INNER JOIN bethadba.geempre ON geempre.codi_emp = HRCLIENTE.CODI_EMP 
            WHERE HRCLIENTE.I_CLIENTE_FIXO IS NOT NULL
        """
        escritorios_raw = fetch_data(query_escritorios)

        listaEscritorios = []
        codigos_existentes = set()
        for e in escritorios_raw:
            codigo = e["codigo_escritorio"]
            if codigo not in codigos_existentes:
                listaEscritorios.append({
                    "nome": e["nome"],
                    "codigo_escritorio": codigo
                })
                codigos_existentes.add(codigo)

        # Buscar clientes
        query_clientes = f"""
        SELECT 
            hc.CODI_EMP AS escritorio,
            hc.I_CLIENTE_FIXO AS id_empresa,
            ISNULL(CONVERT(varchar, ge.dina_emp, 23), 'nada') AS data_inatv,
            ISNULL(CONVERT(varchar, ge.dcad_emp, 23), 'nada') AS data_cadast
        FROM bethadba.HRCLIENTE hc
        INNER JOIN bethadba.geempre ge ON hc.I_CLIENTE_FIXO = ge.codi_emp
        """

        # Queries de importações
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

        clientes = fetch_data(query_clientes)
        saidas = agrupar_por_empresa_mes(fetch_data(query_saida), "data_ref")
        entradas = agrupar_por_empresa_mes(fetch_data(query_entrada), "data_ref")
        servicos = agrupar_por_empresa_mes(fetch_data(query_servicos), "data_ref")
        lancamentos = agrupar_por_empresa_mes(fetch_data(query_lancamentos), "data_ref")
        lancamentos_manuais = agrupar_por_empresa_mes(fetch_data(query_lancamentos_manuais), "data_ref")

        meses = gerar_meses_em_portugues(start_date, end_date)
        faturamento_result = get_faturamento(start_date, end_date)

        # Verificar se o resultado é um JsonResponse (erro)
        if isinstance(faturamento_result, JsonResponse):
            logger.error(f"Erro ao buscar faturamento: {faturamento_result.content}")
            faturamento = []
        else:
            faturamento = faturamento_result

        # Criar dicionário de faturamento por empresa
        faturamento_por_empresa = {}
        for item in faturamento:
            if isinstance(item, dict):  # Verificar se é um dicionário válido
                codi_emp = str(item.get("codi_emp"))
                if codi_emp and "faturamento" in item:
                    faturamento_por_empresa[codi_emp] = item["faturamento"]

        resultados = []

        for escritorio in listaEscritorios:
            contagem_mes = {mes: 0 for mes in meses}

            # Contagem de clientes
            for cliente in clientes:
                if cliente["escritorio"] != escritorio["codigo_escritorio"]:
                    continue

                for mes in meses:
                    if esta_dentro_intervalo(mes, cliente["data_cadast"], cliente["data_inatv"]):
                        contagem_mes[mes] += 1

            # Dados de importações do escritório
            dados_importacoes = {
                "entradas": {},
                "saidas": {},
                "servicos": {},
                "lancamentos": {},
                "lancamentos_manuais": {},
                "porcentagem_lancamentos_manuais": {},
                "total_entradas": 0,
                "total_saidas": 0,
                "total_servicos": 0,
                "total_lancamentos": 0,
                "total_lancamentos_manuais": 0,
                "total_geral": 0
            }

            # Preencher dados de importações
            for mes in meses:
                dados_importacoes["entradas"][mes] = entradas.get(escritorio["codigo_escritorio"], {}).get(mes, 0)
                dados_importacoes["saidas"][mes] = saidas.get(escritorio["codigo_escritorio"], {}).get(mes, 0)
                dados_importacoes["servicos"][mes] = servicos.get(escritorio["codigo_escritorio"], {}).get(mes, 0)
                dados_importacoes["lancamentos"][mes] = lancamentos.get(escritorio["codigo_escritorio"], {}).get(mes, 0)
                dados_importacoes["lancamentos_manuais"][mes] = lancamentos_manuais.get(escritorio["codigo_escritorio"], {}).get(mes, 0)

                # Calcular porcentagem de lançamentos manuais para o mês
                total_lancamentos_mes = dados_importacoes["lancamentos"][mes]
                if total_lancamentos_mes > 0:
                    porcentagem = (dados_importacoes["lancamentos_manuais"][mes] / total_lancamentos_mes) * 100
                    dados_importacoes["porcentagem_lancamentos_manuais"][mes] = f"{porcentagem:.1f}%"
                else:
                    dados_importacoes["porcentagem_lancamentos_manuais"][mes] = "0%"

                dados_importacoes["total_entradas"] += dados_importacoes["entradas"][mes]
                dados_importacoes["total_saidas"] += dados_importacoes["saidas"][mes]
                dados_importacoes["total_servicos"] += dados_importacoes["servicos"][mes]
                dados_importacoes["total_lancamentos"] += dados_importacoes["lancamentos"][mes]
                dados_importacoes["total_lancamentos_manuais"] += dados_importacoes["lancamentos_manuais"][mes]

            # Calcular porcentagem total de lançamentos manuais
            if dados_importacoes["total_lancamentos"] > 0:
                porcentagem_total = (dados_importacoes["total_lancamentos_manuais"] / dados_importacoes["total_lancamentos"]) * 100
                dados_importacoes["porcentagem_total_lancamentos_manuais"] = f"{porcentagem_total:.1f}%"
            else:
                dados_importacoes["porcentagem_total_lancamentos_manuais"] = "0%"

            dados_importacoes["total_geral"] = (
                dados_importacoes["total_entradas"] +
                dados_importacoes["total_saidas"] +
                dados_importacoes["total_servicos"] +
                dados_importacoes["total_lancamentos"]
            )

            # Encontrar o faturamento específico deste escritório
            faturamento_escritorio = next(
                (item for item in faturamento_result if str(item.get("codi_emp")) == str(escritorio["codigo_escritorio"])),
                {"codi_emp": escritorio["codigo_escritorio"], "faturamento": {}}
            )

            resultados.append({
                "escritorio": str(escritorio["nome"]),
                "codigo": int(escritorio["codigo_escritorio"]),
                "clientes": {str(k): int(v) for k, v in contagem_mes.items()},
                "importacoes": dados_importacoes,
                "faturamento": faturamento_escritorio["faturamento"]
            })

        return resultados

    except Exception as e:
        logger.error(f"Erro em get_analise_escritorio: {str(e)}")
        return {"error": str(e)}
