from django.http import JsonResponse
from datetime import datetime, date, time, timedelta
from odbc_reader.services import fetch_data
import calendar

# Lista de meses abreviados em português
MESES_PT = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun',
            'jul', 'ago', 'set', 'out', 'nov', 'dez']

def format_log_time(start_log, end_log):
    if not isinstance(start_log, time) or not isinstance(end_log, time):
        raise ValueError("start_log e end_log precisam ser do tipo datetime.time")

    inicio = datetime.combine(date.min, start_log)
    fim = datetime.combine(date.min, end_log)

    if fim < inicio:
        fim += timedelta(days=1)

    return int((fim - inicio).total_seconds())

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

            if not isinstance(data_log, date):
                raise ValueError(f"data_log não é date: {data_log}")

            mes = data_log.month
            ano = data_log.year
            mes_nome = f"{MESES_PT[mes - 1]}/{ano}"  # exemplo: jan/2024
            tempo = format_log_time(atividade["tini_log"], atividade["tfim_log"])

            if empresa not in resultado:
                resultado[empresa] = {"total": 0}

            if mes_nome not in resultado[empresa]:
                resultado[empresa][mes_nome] = 0

            resultado[empresa][mes_nome] += tempo
            resultado[empresa]["total"] += tempo

        return resultado

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
