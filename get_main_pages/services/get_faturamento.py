from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging
import json

logger = logging.getLogger(__name__)

# Mapeamento manual dos meses abreviados em português
MESES_PT = {
    "jan": 1,
    "fev": 2,
    "mar": 3,
    "abr": 4,
    "mai": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "out": 10,
    "nov": 11,
    "dez": 12,
}
ORDENA_MES_PT = {v: k for k, v in MESES_PT.items()}


def get_faturamento(data_inicial, data_final):
    try:
        query = f"""
            SELECT 
                COALESCE(s.codi_emp, sv.codi_emp) as codi_emp,
                COALESCE(s.mes, sv.mes) as mes,
                COALESCE(s.ano, sv.ano) as ano,
                COALESCE(s.total_saidas, 0) + COALESCE(sv.total_servicos, 0) as total
            FROM (
                SELECT 
                    codi_emp,
                    EXTRACT(MONTH FROM dsai_sai) AS mes,
                    EXTRACT(YEAR FROM dsai_sai) AS ano,
                    SUM(vcon_sai) AS total_saidas
                FROM bethadba.efsaidas
                WHERE dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'
                GROUP BY codi_emp, EXTRACT(YEAR FROM dsai_sai), EXTRACT(MONTH FROM dsai_sai)
            ) s
            FULL OUTER JOIN (
                SELECT 
                    codi_emp,
                    EXTRACT(MONTH FROM dser_ser) AS mes,
                    EXTRACT(YEAR FROM dser_ser) AS ano,
                    SUM(vcon_ser) AS total_servicos
                FROM bethadba.efservicos
                WHERE dser_ser BETWEEN '{data_inicial}' AND '{data_final}'
                  AND NOT EXISTS (
                      SELECT 1 FROM bethadba.efsaidas
                      WHERE efsaidas.codi_emp = efservicos.codi_emp
                        AND efsaidas.dsai_sai = efservicos.dser_ser
                  )
                GROUP BY codi_emp, EXTRACT(YEAR FROM dser_ser), EXTRACT(MONTH FROM dser_ser)
            ) sv
            ON s.codi_emp = sv.codi_emp AND s.mes = sv.mes AND s.ano = sv.ano
            ORDER BY codi_emp, ano, mes
        """

        dados = fetch_data(query)
        if not dados:
            return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

        resultado = {}

        for item in dados:
            if isinstance(item, bytes):
                item = json.loads(item.decode("utf-8"))

            codi_emp = str(item.get("codi_emp"))
            mes = int(item.get("mes"))
            ano = int(item.get("ano"))
            total = float(item.get("total", 0))
            nome_mes = f"{ORDENA_MES_PT[mes]}/{ano}"

            if codi_emp not in resultado:
                resultado[codi_emp] = {}

            if nome_mes not in resultado[codi_emp]:
                resultado[codi_emp][nome_mes] = [0.0, "0%"]

            resultado[codi_emp][nome_mes][0] += round(total, 2)

        # Calcular variação entre os meses
        for codi_emp, fat in resultado.items():
            meses_ordenados = sorted(
                fat.keys(),
                key=lambda x: (int(x.split("/")[1]), MESES_PT[x.split("/")[0]]),
            )

            for i in range(1, len(meses_ordenados)):
                mes_atual = meses_ordenados[i]
                mes_anterior = meses_ordenados[i - 1]

                valor_atual = fat[mes_atual][0]
                valor_anterior = fat[mes_anterior][0]

                if valor_anterior > 0:
                    variacao = ((valor_atual - valor_anterior) / valor_anterior) * 100
                    fat[mes_atual][1] = f"{variacao:.2f}%"
                else:
                    fat[mes_atual][1] = "0%"

            # Garantir que o primeiro mês seja "0%"
            if meses_ordenados:
                fat[meses_ordenados[0]][1] = "0%"

        # Formatar para retorno
        dados_formatados = [
            {"codi_emp": codi_emp, "faturamento": valores}
            for codi_emp, valores in resultado.items()
        ]

        return dados_formatados

    except Exception as e:
        logger.exception("Erro ao processar faturamento com variação.")
        return JsonResponse({"error": str(e)}, status=500)


listaCfop = [
    5000,
    5100,
    5101,
    5102,
    5103,
    5104,
    5105,
    5106,
    5109,
    5110,
    5111,
    5112,
    5113,
    5114,
    5115,
    5116,
    5117,
    5118,
    5119,
    5120,
    5122,
    5123,
    5250,
    5251,
    5252,
    5253,
    5254,
    5255,
    5256,
    5257,
    5258,
    5300,
    5301,
    5302,
    5303,
    5304,
    5305,
    5306,
    5307,
    5350,
    5351,
    5352,
    5353,
    5354,
    5355,
    5356,
    5357,
    5359,
    5360,
    5400,
    5401,
    5402,
    5403,
    5405,
    5550,
    5551,
    5651,
    5652,
    5653,
    5654,
    5655,
    5656,
    5932,
    5933,
    6000,
    6100,
    6101,
    6102,
    6103,
    6104,
    6105,
    6106,
    6107,
    6108,
    6109,
    6110,
    6111,
    6112,
    6113,
    6114,
    6115,
    6116,
    6117,
    6118,
    6119,
    6120,
    6122,
    6123,
    6250,
    6251,
    6252,
    6253,
    6254,
    6255,
    6256,
    6257,
    6258,
    6300,
    6301,
    6302,
    6303,
    6304,
    6305,
    6306,
    6307,
    6350,
    6351,
    6352,
    6353,
    6354,
    6355,
    6356,
    6357,
    6359,
    6400,
    6401,
    6402,
    6403,
    6404,
    6550,
    6551,
    6651,
    6652,
    6653,
    6654,
    6655,
    6656,
    6932,
    6933,
    7000,
    7100,
    7101,
    7102,
    7105,
    7106,
    7127,
    7250,
    7251,
    7300,
    7301,
    7350,
    7358,
]


def get_faturamento_teste(start_date, end_date):
    query = f"""
        SELECT
            efsaidas.codi_emp AS empresa,
            efsaidas.codi_sai AS saida,
            efsaidas.codi_acu AS acumulador,
            efsaidas.codi_nat AS cfop,
            efsaidas.dsai_sai AS data_saida,
            efsaidas.vcon_sai AS valor
        FROM bethadba.efsaidas 
        WHERE codi_emp = 128 
          AND ddoc_sai BETWEEN '{start_date}' AND '{end_date}'
    """

    result = fetch_data(query)
    soma = Decimal('0.00')

    for i in result:
        cfop = i.get("cfop")
        if cfop in listaCfop:
            valor = i.get("valor", 0) or 0
            try:
                valor_num = Decimal(str(valor))
            except (InvalidOperation, ValueError, TypeError):
                valor_num = Decimal('0.00')
            soma += valor_num
            print(soma)

    if not result:
        return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

    return JsonResponse({"soma_valores": float(soma)}, status=200)
