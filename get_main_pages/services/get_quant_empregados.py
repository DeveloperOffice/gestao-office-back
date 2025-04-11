from collections import defaultdict
from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime, date
import calendar

def get_contratados_por_mes(start_date, end_date):
    try:
        query = """
        SELECT
            f.codi_emp,
            f.admissao,
            r.demissao
        FROM bethadba.foempregados f
        LEFT JOIN bethadba.forescisoes r
            ON f.codi_emp = r.codi_emp
            AND f.i_empregados = r.i_empregados
        WHERE f.admissao IS NOT NULL
        """
        result = fetch_data(query)

        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        meses_nome = {
            1: "jan", 2: "fev", 3: "mar", 4: "abr",
            5: "mai", 6: "jun", 7: "jul", 8: "ago",
            9: "set", 10: "out", 11: "nov", 12: "dez"
        }

        # Gera os meses do intervalo
        meses_intervalo = []
        ano_mes = date(start.year, start.month, 1)
        while ano_mes <= end:
            meses_intervalo.append((ano_mes.year, ano_mes.month))
            if ano_mes.month == 12:
                ano_mes = date(ano_mes.year + 1, 1, 1)
            else:
                ano_mes = date(ano_mes.year, ano_mes.month + 1, 1)

        empresas_dict = defaultdict(lambda: defaultdict(int))

        for row in result:
            codi_emp = row["codi_emp"]
            admissao = row["admissao"]
            demissao = row.get("demissao")

            for ano, mes in meses_intervalo:
                fim_mes = date(ano, mes, calendar.monthrange(ano, mes)[1])
                nome_mes = f"{meses_nome[mes]}/{ano}"

                # O funcionário está ativo se foi admitido até o fim do mês
                # e não foi demitido antes ou dentro desse mesmo mês
                if admissao <= fim_mes and (demissao is None or demissao > fim_mes):
                    empresas_dict[codi_emp][nome_mes] += 1

        dados_formatados = [
            {"codi_emp": codi_emp, "quantidade_ativos": meses}
            for codi_emp, meses in empresas_dict.items()
        ]

        return JsonResponse(dados_formatados, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
