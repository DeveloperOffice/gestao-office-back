from django.http import JsonResponse
from datetime import datetime, date, time, timedelta
from odbc_reader.services import fetch_data
import calendar

# Lista de meses abreviados em português
MESES_PT = [
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
]


# Função para formatar o formato do Horário em segundos
def format_log_time(start_date, start_time, end_date, end_time):
    # Combina data e hora em um único datetime
    formato = "%Y-%m-%d %H:%M:%S"

    inicio = datetime.strptime(f"{start_date} {start_time}", formato)
    fim = datetime.strptime(f"{end_date} {end_time}", formato)

    # Calcula a diferença em segundos (sempre positiva)
    return abs(int((fim - inicio).total_seconds()))


def get_atividades_empresa_mes(start_date, end_date):
    try:
        query = f"""
        SELECT
            *
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
            tempo = format_log_time(
                atividade["data_log"],  # Data de início (mesmo dia)
                atividade["tini_log"],  # Hora de início
                atividade["dfim_log"],  # Data real do fim (pode ser diferente)
                atividade["tfim_log"],  # Hora do fim
            )

            if empresa not in resultado:
                resultado[empresa] = {"total": 0}

            if mes_nome not in resultado[empresa]:
                resultado[empresa][mes_nome] = 0

            resultado[empresa][mes_nome] += tempo
            resultado[empresa]["total"] += tempo

        return resultado

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
