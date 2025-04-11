from django.http import JsonResponse
from datetime import datetime, date
from odbc_reader.services import fetch_data
import calendar

from datetime import datetime, date, time, timedelta

def format_log_time(start_log, end_log):
    if not isinstance(start_log, time) or not isinstance(end_log, time):
        raise ValueError("start_log e end_log precisam ser do tipo datetime.time")
    
    # Combina com uma data qualquer só para poder subtrair
    inicio = datetime.combine(date.min, start_log)
    fim = datetime.combine(date.min, end_log)

    # Se o fim for menor que o início, assume que passou da meia-noite
    if fim < inicio:
        fim += timedelta(days=1)

    diferenca_em_segundos = int((fim - inicio).total_seconds())
    return diferenca_em_segundos

def get_atividades_empresa_mes(start_date, end_date):
    try:
        query = f"""
        SELECT
            geloguser.codi_emp,
            geloguser.data_log,
            geloguser.tini_log,
            geloguser.tfim_log
        FROM bethadba.geloguser
        WHERE geloguser.data_log BETWEEN '{start_date}' AND '{end_date}'
        """
        atividades = fetch_data(query)
        
        resultado = {}

        for atividade in atividades:
            empresa = atividade["codi_emp"]
            data_log = atividade["data_log"]

            # Garante que data_log seja um datetime.date
            if not isinstance(data_log, date):
                raise ValueError(f"data_log não é date: {data_log}")

            mes = data_log.month
            mes_nome = calendar.month_abbr[mes].lower()  # 'jan', 'feb', etc.
            tempo = format_log_time(atividade["tini_log"], atividade["tfim_log"])

            if empresa not in resultado:
                resultado[empresa] = {m.lower(): 0 for m in calendar.month_abbr if m}
                resultado[empresa]["total"] = 0

            resultado[empresa][mes_nome] += tempo
            resultado[empresa]["total"] += tempo

        return JsonResponse(resultado)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
