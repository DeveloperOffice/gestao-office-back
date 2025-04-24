from odbc_reader.services import fetch_data
from collections import defaultdict
from datetime import datetime, date, timedelta


def get_socio_aniversariante():
    try:
        today = date.today() #h
        first_day_current = today.replace(day=1)#1 m a
        last_day_prev = first_day_current - timedelta(days=1)# achar o ultimo dia  do mes anter
        start_prev = last_day_prev - timedelta(days=4)# mesma coisa soq com o prox mes
        prev_month = last_day_prev.month
        curr_month = today.month
        if curr_month == 12:
            first_day_next = date(today.year + 1, 1, 1)
        else:
            first_day_next = date(today.year, curr_month + 1, 1)
        next_month = first_day_next.month

        query = f"""
            SELECT 
                q.codi_emp,
                q.i_socio,
                s.nome,
                s.dtnascimento
            FROM bethadba.gequadrosocietario_socios q
            JOIN bethadba.gesocios s 
              ON q.i_socio = s.i_socio
            WHERE s.emancipado = 'N'
        """
        result = fetch_data(query)

        # empresas por sócio e armazena info do sócio
        empresas_por_socio = defaultdict(list)
        socio_info = {}

        for row in result:
            emp = row["codi_emp"]
            socio_id = row["i_socio"]
            nome = row["nome"]
            dtnasc = row.get("dtnascimento")

            empresas_por_socio[socio_id].append(emp)

            if socio_id not in socio_info:
                socio_info[socio_id] = {
                    "nome": nome,
                    "dtnascimento": dtnasc
                }

        # Filtra sócios pela janela e monta o JSON de resposta
        output = []
        for socio_id, info in socio_info.items():
            dtn = info.get("dtnascimento")
            if not dtn:
                continue

            if isinstance(dtn, date):
                birth_dt = dtn
            else:
                try:
                    birth_dt = datetime.strptime(dtn, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    continue

            day, month = birth_dt.day, birth_dt.month

            #organizaçao dos dias
            if not (
                (month == prev_month and start_prev.day <= day <= last_day_prev.day)
                or (month == curr_month)
                or (month == next_month and day <= 5)
            ):
                continue

            # formata ISO YYYY-MM-DD
            formatted_date = birth_dt.strftime("%Y-%m-%d")
            output.append({
                "socio": info["nome"],
                "empresas": empresas_por_socio[socio_id],
                "data_nascimento": formatted_date
            })

        # ordençao
        def _sort_key(item):
            # converte de "YYYY-MM-DD" para date
            dt = datetime.strptime(item["data_nascimento"], "%Y-%m-%d").date()
            m, d = dt.month, dt.day
            if m == prev_month:
                rel = 0
            elif m == curr_month:
                rel = 1
            else:
                rel = 2
            return (rel, d) 
        output.sort(key=_sort_key)

        return output

    except Exception as e:
        return {"error": str(e)}
