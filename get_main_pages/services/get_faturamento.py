from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging
import json

logger = logging.getLogger(__name__)

listaCfopDevolucao = [1200, 1201, 1202, 1203, 1204, 1553, 1660, 1661, 1662, 
                      2200, 2201, 2202, 2203, 2204, 2410, 2411, 2553, 2660, 
                      2661, 2662, 3200, 3201, 3202, 3211, 3503, 3553]

listaCfop = [
    5000, 5100, 5101, 5102, 5103, 5104, 5105, 5106, 5109,
    5110, 5111, 5112, 5113, 5114, 5115, 5116, 5117, 5118,
    5119, 5120, 5122, 5123, 5250, 5251, 5252, 5253, 5254,
    5255, 5256, 5257, 5258, 5300, 5301, 5302, 5303, 5304,
    5305, 5306, 5307, 5350, 5351, 5352, 5353, 5354, 5355,
    5356, 5357, 5359, 5360, 5400, 5401, 5402, 5403, 5405,
    5550, 5551, 5651, 5652, 5653, 5654, 5655, 5656, 5932,
    5933, 5949, 6000, 6100, 6101, 6102, 6103, 6104, 6105, 
    6106, 6107, 6108, 6109, 6110, 6111, 6112, 6113, 6114, 
    6115, 6116, 6117, 6118, 6119, 6120, 6122, 6123, 6250, 
    6251, 6252, 6253, 6254, 6255, 6256, 6257, 6258, 6300, 
    6301, 6302, 6303, 6304, 6305, 6306, 6307, 6350, 6351, 
    6352, 6353, 6354, 6355, 6356, 6357, 6359, 6400, 6401, 
    6402, 6403, 6404, 6550, 6551, 6651, 6652, 6653, 6654, 
    6655, 6656, 6932, 6933, 7000, 7100, 7101, 7102, 7105, 
    7106, 7127, 7250, 7251, 7300, 7301, 7350, 7358, 
]

MESES_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}
ORDENA_MES_PT = {v: k for k, v in MESES_PT.items()}

def get_faturamento(data_inicial, data_final):
    try:
        # 1) Buscar todas as saídas
        query_s = f"""
            SELECT codi_emp, dsai_sai AS data, vcon_sai AS valor, codi_nat AS cfop
            FROM bethadba.efsaidas
            WHERE dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'
        """
        rows_s = fetch_data(query_s)

        # 2) Buscar todos os serviços
        query_sv = f"""
            SELECT codi_emp, dser_ser AS data, vcon_ser AS valor
            FROM bethadba.efservicos
            WHERE dser_ser BETWEEN '{data_inicial}' AND '{data_final}'
        """
        rows_sv = fetch_data(query_sv)

        # 3) Buscar todas as notas de entrada (devoluções)
        query_e = f"""
            SELECT codi_emp, dent_ent AS data, vcon_ent AS valor, codi_nat AS cfop
            FROM bethadba.efentradas
            WHERE dent_ent BETWEEN '{data_inicial}' AND '{data_final}'
        """
        rows_e = fetch_data(query_e)

        if not rows_s and not rows_sv and not rows_e:
            return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

        resultado = {}
        saidas_set = set()

        # Processa SAÍDAS: registra datas e agrega somente CFOPs válidos
        for item in rows_s:
            if isinstance(item, bytes):
                item = json.loads(item.decode("utf-8"))

            codi_emp = str(item.get("codi_emp"))
            raw_date = item.get("data")
            cfop = item.get("cfop")
            valor = item.get("valor") or 0

            # converte para date
            data_dt = (
                datetime.fromisoformat(raw_date).date()
                if isinstance(raw_date, str)
                else raw_date
            )
            saidas_set.add((codi_emp, data_dt))

            try:
                cfop_int = int(cfop)
            except Exception:
                continue
            if cfop_int not in listaCfop:
                continue

            mes = data_dt.month
            ano = data_dt.year
            nome_mes = f"{ORDENA_MES_PT[mes]}/{ano}"

            resultado.setdefault(codi_emp, {})
            resultado[codi_emp].setdefault(nome_mes, [0.0, "0%"])
            resultado[codi_emp][nome_mes][0] += float(valor)

        # Processa SERVIÇOS: só se não houve saída no mesmo dia
        for item in rows_sv:
            if isinstance(item, bytes):
                item = json.loads(item.decode("utf-8"))

            codi_emp = str(item.get("codi_emp"))
            raw_date = item.get("data")
            valor = item.get("valor") or 0

            data_dt = (
                datetime.fromisoformat(raw_date).date()
                if isinstance(raw_date, str)
                else raw_date
            )
            if (codi_emp, data_dt) in saidas_set:
                continue

            mes = data_dt.month
            ano = data_dt.year
            nome_mes = f"{ORDENA_MES_PT[mes]}/{ano}"

            resultado.setdefault(codi_emp, {})
            resultado[codi_emp].setdefault(nome_mes, [0.0, "0%"])
            resultado[codi_emp][nome_mes][0] += float(valor)

        # Processa ENTRADAS (devoluções): subtrai somente CFOPs de devolução
        for item in rows_e:
            if isinstance(item, bytes):
                item = json.loads(item.decode("utf-8"))

            codi_emp = str(item.get("codi_emp"))
            raw_date = item.get("data")
            cfop = item.get("cfop")
            valor = item.get("valor") or 0

            data_dt = (
                datetime.fromisoformat(raw_date).date()
                if isinstance(raw_date, str)
                else raw_date
            )

            try:
                cfop_int = int(cfop)
            except Exception:
                continue
            if cfop_int not in listaCfopDevolucao:
                continue

            mes = data_dt.month
            ano = data_dt.year
            nome_mes = f"{ORDENA_MES_PT[mes]}/{ano}"

            # inicializa se necessário
            resultado.setdefault(codi_emp, {})
            resultado[codi_emp].setdefault(nome_mes, [0.0, "0%"])
            # subtrai o valor da devolução
            resultado[codi_emp][nome_mes][0] -= float(valor)

        # 4) Calcula variação mês a mês
        for codi_emp, fat in resultado.items():
            meses_ordenados = sorted(
                fat.keys(),
                key=lambda x: (int(x.split("/")[1]), MESES_PT[x.split("/")[0]])
            )

            for i in range(1, len(meses_ordenados)):
                atual = meses_ordenados[i]
                anterior = meses_ordenados[i - 1]
                val_atual = fat[atual][0]
                val_ant = fat[anterior][0]
                if val_ant != 0:
                    pct = (val_atual - val_ant) / val_ant * 100
                    fat[atual][1] = f"{pct:.2f}%"
                else:
                    fat[atual][1] = "0%"

            if meses_ordenados:
                fat[meses_ordenados[0]][1] = "0%"

        # 5) Formata saída como lista de dicts
        return [
            {"codi_emp": codi_emp, "faturamento": valores}
            for codi_emp, valores in resultado.items()
        ]

    except Exception as e:
        logger.exception("Erro ao processar faturamento com variação.")
        return JsonResponse({"error": str(e)}, status=500)

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
        WHERE codi_emp = 1332 
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
