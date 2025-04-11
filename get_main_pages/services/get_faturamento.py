from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_faturamento(data_inicial, data_final):
    try:
        query = f"""
            WITH dados_saidas AS (
                SELECT 
                    codi_emp,
                    EXTRACT(MONTH FROM dsai_sai) as mes,
                    SUM(vcon_sai) as total_saidas
                FROM bethadba.efsaidas
                WHERE dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'
                GROUP BY codi_emp, EXTRACT(MONTH FROM dsai_sai)
            ),
            dados_servicos AS (
                SELECT 
                    codi_emp,
                    EXTRACT(MONTH FROM dser_ser) as mes,
                    SUM(vcon_ser) as total_servicos
                FROM bethadba.efservicos
                WHERE dser_ser BETWEEN '{data_inicial}' AND '{data_final}'
                  AND NOT EXISTS (
                      SELECT 1 FROM bethadba.efsaidas
                      WHERE efsaidas.codi_emp = efservicos.codi_emp
                        AND efsaidas.dsai_sai = efservicos.dser_ser
                  )
                GROUP BY codi_emp, EXTRACT(MONTH FROM dser_ser)
            )
            SELECT 
                COALESCE(s.codi_emp, sv.codi_emp) as codi_emp,
                COALESCE(s.mes, sv.mes) as mes,
                COALESCE(s.total_saidas, 0) + COALESCE(sv.total_servicos, 0) as total
            FROM dados_saidas s
            FULL OUTER JOIN dados_servicos sv 
                ON s.codi_emp = sv.codi_emp AND s.mes = sv.mes
            ORDER BY codi_emp, mes
        """

        dados = fetch_data(query)
        if not dados:
            return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

        meses_nome = {
            1: "jan", 2: "fev", 3: "mar", 4: "abr",
            5: "mai", 6: "jun", 7: "jul", 8: "ago",
            9: "set", 10: "out", 11: "nov", 12: "dez"
        }

        # Filtrar apenas os meses entre data_inicial e data_final
        try:
            di = datetime.strptime(data_inicial, "%Y-%m-%d")
            df = datetime.strptime(data_final, "%Y-%m-%d")
            meses_intervalo = {}

            if di.year == df.year:
                for m in range(di.month, df.month + 1):
                    meses_intervalo[m] = meses_nome[m]
            else:
                for m in range(di.month, 13):
                    meses_intervalo[m] = meses_nome[m]
                for m in range(1, df.month + 1):
                    meses_intervalo[m] = meses_nome[m]
        except Exception as e:
            logger.warning("Erro ao interpretar datas, usando todos os meses.")
            meses_intervalo = meses_nome

        resultado = {}

        for item in dados:
            codi_emp = str(item.get("codi_emp"))
            mes_num = int(item.get("mes"))
            valor = float(item.get("total", 0))
            nome_mes = meses_nome.get(mes_num)

            if not nome_mes or mes_num not in meses_intervalo:
                continue

            if codi_emp not in resultado:
                resultado[codi_emp] = {nome: [0.0, "0%"] for nome in meses_intervalo.values()}

            resultado[codi_emp][nome_mes][0] += round(valor, 2)

        # Calcular a variação mês a mês
        meses_ordenados = sorted(meses_intervalo.items(), key=lambda x: x[0])  # [(1, 'jan'), (2, 'fev'), ...]

        for codi_emp, fat in resultado.items():
            for i in range(1, len(meses_ordenados)):
                mes_atual = meses_ordenados[i][1]
                mes_anterior = meses_ordenados[i - 1][1]

                valor_atual = fat[mes_atual][0]
                valor_anterior = fat[mes_anterior][0]

                if valor_anterior > 0:
                    variacao = ((valor_atual - valor_anterior) / valor_anterior) * 100
                    fat[mes_atual][1] = f"{variacao:.2f}%"
                else:
                    fat[mes_atual][1] = "0%"

            # Garante que o primeiro mês tenha variação "0%"
            if meses_ordenados:
                primeiro_mes = meses_ordenados[0][1]
                fat[primeiro_mes][1] = "0%"

        # Reorganizar para lista final
        dados_formatados = [
            {
                "codi_emp": codi_emp,
                "faturamento": valores
            }
            for codi_emp, valores in resultado.items()
        ]

        return dados_formatados

    except Exception as e:
        logger.exception("Erro ao processar faturamento com variação.")
        return JsonResponse({"error": str(e)}, status=500)
