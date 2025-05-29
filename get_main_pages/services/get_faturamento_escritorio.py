from datetime import datetime
from django.http import JsonResponse
from odbc_reader.services import fetch_data
import logging

logger = logging.getLogger(__name__)

# CFOPs de devolução (entradas que devem ser subtraídas)
CFOP_DEVOLUCAO = {
    1200, 1201, 1202, 1203, 1204, 1553, 1660, 1661, 1662,
    2200, 2201, 2202, 2203, 2204, 2410, 2411, 2553, 2660,
    2661, 2662, 3200, 3201, 3202, 3211, 3503, 3553
}

# CFOPs válidos para faturamento (saídas e serviços)
CFOP_FATURAMENTO = {
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
    7106, 7127, 7250, 7251, 7300, 7301, 7350, 7358
}

# Mapeamento de meses em PT e inverso
MESES_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}
ORDENA_MES_PT = {v: k for k, v in MESES_PT.items()}


def get_faturamento(data_inicial, data_final, listaEscritorios):
    """
    Retorna lista de dicts com faturamento mensal de cada empresa no intervalo.
    Executa uma única query com UNION ALL / GROUP BY e calcula variação em Python.
    """
    escritorios_sql = ", ".join(map(str, listaEscritorios))

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
             AND codi_emp IN ({escritorios_sql})

          UNION ALL

          -- serviços
          SELECT codi_emp, dser_ser AS data, vcon_ser AS valor
            FROM bethadba.efservicos
           WHERE dser_ser BETWEEN '{data_inicial}' AND '{data_final}'
             AND codi_emp IN ({escritorios_sql})

          UNION ALL

          -- devoluções (negativo)
          SELECT codi_emp, dent_ent AS data, -vcon_ent AS valor
            FROM bethadba.efentradas
           WHERE dent_ent BETWEEN '{data_inicial}' AND '{data_final}'
             AND codi_emp IN ({escritorios_sql})
             AND codi_nat IN ({','.join(map(str, CFOP_DEVOLUCAO))})

          UNION ALL

          -- cupons (sinal conforme situação)
          SELECT CODI_EMP AS codi_emp, DATA_CFE AS data,
                 CASE WHEN SITUACAO IN (2,4)
                      THEN -VALOR_TOTAL_CFE ELSE VALOR_TOTAL_CFE END AS valor
            FROM bethadba.EFCUPOM_FISCAL_ELETRONICO
           WHERE DATA_CFE BETWEEN '{data_inicial}' AND '{data_final}'
             AND CODI_EMP IN ({escritorios_sql})
        ) AS todas
        GROUP BY codi_emp, YEAR(data), MONTH(data)
        ORDER BY codi_emp, YEAR(data), MONTH(data)
        """

        rows = fetch_data(sql)

        # Reconstrói o dicionário no formato antigo
        resultado = {}
        for r in rows:
            emp     = str(r['codi_emp'])
            mes_ano = f"{ORDENA_MES_PT[int(r['mes'])]}/{int(r['ano'])}"
            total   = float(r['total'])
            resultado.setdefault(emp, {})[mes_ano] = [total, '0%']

        # Calcula variação mensal
        for fat in resultado.values():
            _calcula_variacao(fat)

        return [
            {'codi_emp': emp, 'faturamento': fat}
            for emp, fat in resultado.items()
        ]

    except Exception:
        logger.exception('Erro no cálculo de faturamento')
        raise


def _calcula_variacao(fat):
    """
    Recebe um dict { 'mes/ano': [valor, '%variação'] }, calcula variação entre meses.
    """
    meses = sorted(
        fat.keys(),
        key=lambda x: (int(x.split('/')[1]), MESES_PT[x.split('/')[0]])
    )
    for i in range(1, len(meses)):
        cur, prev = meses[i], meses[i - 1]
        ant = fat[prev][0]
        diff = fat[cur][0] - ant
        fat[cur][1] = f"{(diff / ant * 100) if ant else 0:.2f}%"
    if meses:
        fat[meses[0]][1] = '0%'
