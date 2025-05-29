from datetime import datetime
from decimal import Decimal
from django.http import JsonResponse
from odbc_reader.services import fetch_data
import logging
import json

logger = logging.getLogger(__name__)

# CFOPs de devolução (entradas que devem ser subtraídas)
listaCfopDevolucao = [
    1200, 1201, 1202, 1203, 1204, 1553, 1660, 1661, 1662,
    2200, 2201, 2202, 2203, 2204, 2410, 2411, 2553, 2660,
    2661, 2662, 3200, 3201, 3202, 3211, 3503, 3553
]

# CFOPs válidos para faturamento (saídas e serviços)
listaCfop = [
    5000, 5100, 5101, 5102, 5103, 5104, 5105, 5106, 5109,
    5110, 5111, 5112, 5113, 5114, 5115, 5116, 5117, 5118,
    5119, 5120, 5122, 5123, 5250, 5251, 5252, 5253, 5254,
    5255, 5256, 5257, 5258, 5300, 5301, 5302, 5303, 5304,
    5305, 5306, 5307, 5350, 5351, 5352, 5353, 5354, 5355,
    5356, 5357, 5359, 5360, 5400, 5401, 5402, 5403, 5405,
    5550, 5551, 5651, 5652, 5653, 5654, 5655, 5656, 5932,
    5933,  6000, 6100, 6101, 6102, 6103, 6104, 6105, 
    6106, 6107, 6108, 6109, 6110, 6111, 6112, 6113, 6114, 
    6115, 6116, 6117, 6118, 6119, 6120, 6122, 6123, 6250, 
    6251, 6252, 6253, 6254, 6255, 6256, 6257, 6258, 6300, 
    6301, 6302, 6303, 6304, 6305, 6306, 6307, 6350, 6351, 
    6352, 6353, 6354, 6355, 6356, 6357, 6359, 6400, 6401, 
    6402, 6403, 6404, 6550, 6551, 6651, 6652, 6653, 6654, 
    6655, 6656, 6932, 6933, 7000, 7100, 7101, 7102, 7105, 
    7106, 7127, 7250, 7251, 7300, 7301, 7350, 7358, 
]

# Mapeamento de meses em PT e inverso
MESES_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}
ORDENA_MES_PT = {v: k for k, v in MESES_PT.items()}

def get_faturamento(data_inicial, data_final):
    """
    Retorna lista de dicts com faturamento mensal de cada empresa no intervalo,
    e para company_id imprime o total de saídas, serviços, devoluções e cupons.
    """
    # Empresa que queremos testar
    company_id = '1332'

    # Totais por tipo, só para company_id
    totais = {
        'saidas': 0.0,
        'servicos': 0.0,
        'devolucoes': 0.0,
        'cupons': 0.0
    }

    try:
        # Consultas
        query_s = f"""
            SELECT codi_emp, dsai_sai AS data, vcon_sai AS valor, codi_nat AS cfop
            FROM bethadba.efsaidas
            WHERE dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'
        """
        query_sv = f"""
            SELECT codi_emp, dser_ser AS data, vcon_ser AS valor
            FROM bethadba.efservicos
            WHERE dser_ser BETWEEN '{data_inicial}' AND '{data_final}'
        """
        query_e = f"""
            SELECT codi_emp, dent_ent AS data, vcon_ent AS valor, codi_nat AS cfop
            FROM bethadba.efentradas
            WHERE dent_ent BETWEEN '{data_inicial}' AND '{data_final}'
        """
        query_cf = f"""
            SELECT CODI_EMP AS codi_emp, DATA_CFE AS data,
                   SITUACAO AS situacao, VALOR_TOTAL_CFE AS valor
            FROM bethadba.EFCUPOM_FISCAL_ELETRONICO
            WHERE DATA_CFE BETWEEN '{data_inicial}' AND '{data_final}'
        """

        rows_s  = fetch_data(query_s)
        rows_sv = fetch_data(query_sv)
        rows_e  = fetch_data(query_e)
        rows_cf = fetch_data(query_cf)

        if not any([rows_s, rows_sv, rows_e, rows_cf]):
            return []

        resultado = {}
        saidas_set = set()

        # Processa saídas
        for item in _decode_rows(rows_s):
            emp   = str(item['codi_emp'])
            dt    = _parse_date(item['data'])
            cf    = _to_int(item.get('cfop'))
            valor = float(item.get('valor', 0))
            if cf not in listaCfop:
                continue
            saidas_set.add((emp, dt))
            _acumula(resultado, emp, dt, valor)

            if emp == company_id:
                totais['saidas'] += valor

        # Processa serviços
        for item in _decode_rows(rows_sv):
            emp   = str(item['codi_emp'])
            dt    = _parse_date(item['data'])
            valor = float(item.get('valor', 0))
            if (emp, dt) in saidas_set:
                continue
            _acumula(resultado, emp, dt, valor)

            if emp == company_id:
                totais['servicos'] += valor

        # Processa devoluções
        for item in _decode_rows(rows_e):
            emp   = str(item['codi_emp'])
            dt    = _parse_date(item['data'])
            cf    = _to_int(item.get('cfop'))
            valor = float(item.get('valor', 0))
            if cf not in listaCfopDevolucao:
                continue
            _acumula(resultado, emp, dt, -valor)

            if emp == company_id:
                totais['devolucoes'] += valor  # acumulamos o valor positivo para relatórios

        # Processa cupons fiscais
        for item in _decode_rows(rows_cf):
            emp      = str(item['codi_emp'])
            dt       = _parse_date(item['data'])
            valor    = float(item.get('valor', 0))
            situacao = item.get('situacao')
            ajuste   = -valor if situacao in (2, 4) else valor
            _acumula(resultado, emp, dt, ajuste)

            if emp == company_id:
                totais['cupons'] += ajuste

        # Calcula variação mensal
        for fat in resultado.values():
            _calcula_variacao(fat)

        # Imprime os totais para a empresa de teste
        # print(f"--- Totais para a empresa {company_id} ---")
        # print(f"Saídas:       {totais['saidas']:.2f}")
        # print(f"Serviços:     {totais['servicos']:.2f}")
        # print(f"Devoluções:   {totais['devolucoes']:.2f}")
        # print(f"Cupons:       {totais['cupons']:.2f}")
        # print("----------------------------------------")

        # Retorna estrutura original
        return [
            {'codi_emp': emp, 'faturamento': vals}
            for emp, vals in resultado.items()
        ]

    except Exception:
        logger.exception('Erro no cálculo de faturamento')
        raise

# Helpers (sem alterações)
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

from decimal import Decimal, InvalidOperation

def get_faturamento_teste(start_date, end_date):
    """
    Soma todas as saídas, serviços, entradas de devolução e cupons fiscais no intervalo,
    reportando totais, quantidades e detalhes:
      - total_saidas e count_saidas
      - total_servicos e count_servicos
      - total_entradas_descontadas e count_entradas_descontadas
      - total_cupons_adicionados e count_cupons_adicionados
      - total_cupons_descontados e count_cupons_descontados
      - total: valor geral após todos ajustes
    """
    # Consultas para cada tipo de nota
    query_s = f"""
        SELECT vcon_sai AS valor
        FROM bethadba.efsaidas
        WHERE codi_emp = 1332
          AND ddoc_sai BETWEEN '{start_date}' AND '{end_date}'
    """
    query_sv = f"""
        SELECT vcon_ser AS valor
        FROM bethadba.efservicos
        WHERE codi_emp = 1332
          AND dser_ser BETWEEN '{start_date}' AND '{end_date}'
    """
    query_e = f"""
        SELECT vcon_ent AS valor, codi_nat AS cfop
        FROM bethadba.efentradas
        WHERE codi_emp = 1332
          AND dent_ent BETWEEN '{start_date}' AND '{end_date}'
    """
    query_cf = f"""
        SELECT VALOR_TOTAL_CFE AS valor, SITUACAO AS situacao
        FROM bethadba.EFCUPOM_FISCAL_ELETRONICO
        WHERE CODI_EMP = 1332
          AND DATA_CFE BETWEEN '{start_date}' AND '{end_date}'
    """

    rows_s  = fetch_data(query_s)
    rows_sv = fetch_data(query_sv)
    rows_e  = fetch_data(query_e)
    rows_cf = fetch_data(query_cf)

    def to_decimal(raw):
        try:
            return Decimal(str(raw or 0))
        except:
            return Decimal('0.00')

    total = Decimal('0.00')
    # iniciais de cada categoria
    total_saidas = total_servicos = total_entradas_sub = total_cupons_add = total_cupons_sub = Decimal('0.00')
    count_saidas = count_servicos = count_entradas_sub = count_cupons_add = count_cupons_sub = 0

    # Saídas
    for row in rows_s:
        valor = to_decimal(row.get('valor'))
        total += valor
        total_saidas += valor
        count_saidas += 1

    # Serviços
    for row in rows_sv:
        valor = to_decimal(row.get('valor'))
        total += valor
        total_servicos += valor
        count_servicos += 1

    # Entradas de devolução (subtraídas)
    for row in rows_e:
        cfop = _to_int(row.get('cfop'))
        if cfop in listaCfopDevolucao:
            valor = to_decimal(row.get('valor'))
            total -= valor
            total_entradas_sub += valor
            count_entradas_sub += 1

    # Cupons fiscais
    for row in rows_cf:
        valor = to_decimal(row.get('valor'))
        situacao = row.get('situacao')
        if situacao in (2, 4):
            total -= valor
            total_cupons_sub += valor
            count_cupons_sub += 1
        else:
            total += valor
            total_cupons_add += valor
            count_cupons_add += 1

    if total == Decimal('0.00'):
        return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

    # Retorna JSON com detalhes
    return JsonResponse({
        'total': float(total),
        'total_saidas': float(total_saidas), 'count_saidas': count_saidas,
        'total_servicos': float(total_servicos), 'count_servicos': count_servicos,
        'total_entradas_descontadas': float(total_entradas_sub), 'count_entradas_descontadas': count_entradas_sub,
        'total_cupons_adicionados': float(total_cupons_add), 'count_cupons_adicionados': count_cupons_add,
        'total_cupons_descontados': float(total_cupons_sub), 'count_cupons_descontados': count_cupons_sub
    }, status=200)


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