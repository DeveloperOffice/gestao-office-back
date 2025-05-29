from datetime import datetime
from decimal import Decimal
from django.http import JsonResponse
from odbc_reader.services import fetch_data
import logging
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# CFOPs de devolução (entradas que devem ser subtraídas)
CFOP_DEVOLUCAO = set([
    1200, 1201, 1202, 1203, 1204, 1553, 1660, 1661, 1662,
    2200, 2201, 2202, 2203, 2204, 2410, 2411, 2553, 2660,
    2661, 2662, 3200, 3201, 3202, 3211, 3503, 3553
])

# CFOPs válidos para faturamento (saídas e serviços)
CFOP_FATURAMENTO = set([
    5000, 5100, 5101, 5102, 5103, 5104, 5105, 5106, 5109,
    5110, 5111, 5112, 5113, 5114, 5115, 5116, 5117, 5118,
    5119, 5120, 5122, 5123, 5250, 5251, 5252, 5253, 5254,
    5255, 5256, 5257, 5258, 5300, 5301, 5302, 5303, 5304,
    5305, 5306, 5307, 5350, 5351, 5352, 5353, 5354, 5355,
    5356, 5357, 5359, 5360, 5400, 5401, 5402, 5403, 5405,
    5550, 5551, 5651, 5652, 5653, 5654, 5655, 5656, 5932,
    5933, 6000, 6100, 6101, 6102, 6103, 6104, 6105,
    6106, 6107, 6108, 6109, 6110, 6111, 6112, 6113, 6114,
    6115, 6116, 6117, 6118, 6119, 6120, 6122, 6123, 6250,
    6251, 6252, 6253, 6254, 6255, 6256, 6257, 6258, 6300,
    6301, 6302, 6303, 6304, 6305, 6306, 6307, 6350, 6351,
    6352, 6353, 6354, 6355, 6356, 6357, 6359, 6400, 6401,
    6402, 6403, 6404, 6550, 6551, 6651, 6652, 6653, 6654,
    6655, 6656, 6932, 6933, 7000, 7100, 7101, 7102, 7105,
    7106, 7127, 7250, 7251, 7300, 7301, 7350, 7358,
])

# Mapeamento de meses em PT e inverso
MESES_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}
ORDENA_MES_PT = {v: k for k, v in MESES_PT.items()}

def get_faturamento(data_inicial, data_final):
    """
    Agrupa todas as operações num único UNION, soma por empresa/ano/mês
    e calcula variação percentual em Python.
    """
    company_id = '1332'
    try:
        sql = f"""
        SELECT
          codi_emp,
          YEAR(data)  AS ano,
          MONTH(data) AS mes,
          ROUND(SUM(valor), 2) AS total
        FROM (
          -- saídas válidas
          SELECT codi_emp, dsai_sai AS data,
                 CASE WHEN codi_nat IN ({','.join(map(str, CFOP_FATURAMENTO))})
                      THEN vcon_sai ELSE 0 END AS valor
            FROM bethadba.efsaidas
           WHERE dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'

          UNION ALL

          -- serviços
          SELECT codi_emp, dser_ser AS data, vcon_ser AS valor
            FROM bethadba.efservicos
           WHERE dser_ser BETWEEN '{data_inicial}' AND '{data_final}'

          UNION ALL

          -- devoluções
          SELECT codi_emp, dent_ent AS data, -vcon_ent AS valor
            FROM bethadba.efentradas
           WHERE dent_ent BETWEEN '{data_inicial}' AND '{data_final}'
             AND codi_nat IN ({','.join(map(str, CFOP_DEVOLUCAO))})

          UNION ALL

          -- cupons
          SELECT CODI_EMP AS codi_emp, DATA_CFE AS data,
                 CASE WHEN SITUACAO IN (2,4)
                      THEN -VALOR_TOTAL_CFE ELSE VALOR_TOTAL_CFE END AS valor
            FROM bethadba.EFCUPOM_FISCAL_ELETRONICO
           WHERE DATA_CFE BETWEEN '{data_inicial}' AND '{data_final}'
        ) AS todas
        GROUP BY codi_emp, YEAR(data), MONTH(data)
        ORDER BY codi_emp, YEAR(data), MONTH(data)
        """

        rows = fetch_data(sql)

        # Reconstrói o dicionário no formato original
        resultado = {}
        for r in rows:
            emp     = str(r['codi_emp'])
            mes_ano = f"{ORDENA_MES_PT[int(r['mes'])]}/{int(r['ano'])}"
            total   = float(r['total'])
            resultado.setdefault(emp, {})[mes_ano] = [total, '0%']

        # Calcula variação mensal em Python
        for fat in resultado.values():
            _calcula_variacao(fat)

        return [
            {'codi_emp': emp, 'faturamento': fat}
            for emp, fat in resultado.items()
        ]

    except Exception:
        logger.exception('Erro no cálculo de faturamento')
        raise




def get_faturamento_teste(start_date, end_date):
    """
    Soma todas as saídas, serviços, entradas de devolução e cupons fiscais no intervalo,
    usando agregações no próprio SQL para reduzir transferência de dados.
    """
    try:
        # consultas agregadas diretamente no banco
        query_s = f"""
            SELECT COUNT(*) AS count_saidas,
                   COALESCE(SUM(vcon_sai), 0) AS total_saidas
            FROM bethadba.efsaidas
            WHERE codi_emp = 1332
              AND ddoc_sai BETWEEN '{start_date}' AND '{end_date}'
        """
        query_sv = f"""
            SELECT COUNT(*) AS count_servicos,
                   COALESCE(SUM(vcon_ser), 0) AS total_servicos
            FROM bethadba.efservicos
            WHERE codi_emp = 1332
              AND dser_ser BETWEEN '{start_date}' AND '{end_date}'
        """
        query_e = f"""
            SELECT COUNT(*) AS count_entradas_sub,
                   COALESCE(SUM(vcon_ent), 0) AS total_entradas_sub
            FROM bethadba.efentradas
            WHERE codi_emp = 1332
              AND dent_ent BETWEEN '{start_date}' AND '{end_date}'
              AND codi_nat IN ({','.join(map(str, CFOP_DEVOLUCAO))})
        """
        query_cf = f"""
            SELECT
              COUNT(CASE WHEN situacao IN (2,4) THEN 1 END) AS count_cupons_sub,
              COALESCE(SUM(CASE WHEN situacao IN (2,4) THEN VALOR_TOTAL_CFE END), 0) AS total_cupons_sub,
              COUNT(CASE WHEN situacao NOT IN (2,4) THEN 1 END) AS count_cupons_add,
              COALESCE(SUM(CASE WHEN situacao NOT IN (2,4) THEN VALOR_TOTAL_CFE END), 0) AS total_cupons_add
            FROM bethadba.EFCUPOM_FISCAL_ELETRONICO
            WHERE CODI_EMP = 1332
              AND DATA_CFE BETWEEN '{start_date}' AND '{end_date}'
        """

        # executar as quatro consultas em paralelo
        with ThreadPoolExecutor(max_workers=4) as ex:
            res_s, res_sv, res_e, res_cf = ex.map(
                lambda q: fetch_data(q)[0],
                (query_s, query_sv, query_e, query_cf)
            )

        # calcula total geral já levando em conta adições e subtrações
        total = (
            Decimal(res_s['total_saidas'])
          + Decimal(res_sv['total_servicos'])
          - Decimal(res_e['total_entradas_sub'])
          + Decimal(res_cf['total_cupons_add'])
          - Decimal(res_cf['total_cupons_sub'])
        )

        if total == Decimal('0.00'):
            return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

        return JsonResponse({
            'total': float(total),
            'total_saidas': float(res_s['total_saidas']),
            'count_saidas': res_s['count_saidas'],
            'total_servicos': float(res_sv['total_servicos']),
            'count_servicos': res_sv['count_servicos'],
            'total_entradas_descontadas': float(res_e['total_entradas_sub']),
            'count_entradas_descontadas': res_e['count_entradas_sub'],
            'total_cupons_adicionados': float(res_cf['total_cupons_add']),
            'count_cupons_adicionados': res_cf['count_cupons_add'],
            'total_cupons_descontados': float(res_cf['total_cupons_sub']),
            'count_cupons_descontados': res_cf['count_cupons_sub']
        }, status=200)

    except Exception:
        logger.exception('Erro no cálculo de faturamento de teste')
        raise



# Helpers
#undefinied_fetch_data = fetch_data  # para evitar linter que reclama de fetch_data

def _decode_rows(rows):
    for r in rows:
        if isinstance(r, bytes):
            yield json.loads(r.decode('utf-8'))
        else:
            yield r


def _parse_date(raw):
    return datetime.fromisoformat(raw).date() if isinstance(raw, str) else raw


def _to_int(val):
    try:
        return int(val)
    except:
        return None


def _acumula(resultado, emp, dt, valor):
    mes, ano = dt.month, dt.year
    chave = f"{ORDENA_MES_PT[mes]}/{ano}"
    resultado.setdefault(emp, {}).setdefault(chave, [0.0, '0%'])
    resultado[emp][chave][0] += valor


def _calcula_variacao(fat):
    meses = sorted(fat.keys(), key=lambda x: (int(x.split('/')[1]), MESES_PT[x.split('/')[0]]))
    for i in range(1, len(meses)):
        cur, prev = meses[i], meses[i-1]
        ant = fat[prev][0]
        diff = fat[cur][0] - ant
        fat[cur][1] = f"{(diff/ant*100) if ant else 0:.2f}%"
    if meses:
        fat[meses[0]][1] = '0%'