from datetime import datetime
import calendar
from odbc_reader.services import fetch_data

def get_novos_mes(start_date, end_date):
    try:
        # Inicializa o dicionário para armazenar o número de empresas por mês
        empresas_por_mes = {}

        # Converte start_date e end_date para datetime
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Consulta para pegar todas as empresas cadastradas até o final de cada mês dentro do intervalo
        query = f"""
        SELECT 
            EXTRACT(YEAR FROM dcad_emp) AS ano,
            EXTRACT(MONTH FROM dcad_emp) AS mes,
            COUNT(codi_emp) AS total_empresas
        FROM bethadba.geempre
        WHERE stat_emp = 'A'
        AND dcad_emp <= '{end_date.strftime('%Y-%m-%d')}'  -- Empresas com data de cadastro até a data final
        GROUP BY ano, mes
        ORDER BY ano, mes
        """
        
        # Aqui, a função fetch_data vai retornar os resultados da consulta
        result = fetch_data(query)

        # Processa os resultados e conta as empresas ativas até o final de cada mês no intervalo
        for row in result:
            mes_ano = f"{calendar.month_abbr[int(row['mes'])].lower()}/{int(row['ano'])}"

            # Verifica se o mês está dentro do intervalo de start_date e end_date
            mes_ref = datetime(row['ano'], int(row['mes']), 1)
            if start_date <= mes_ref <= end_date:
                empresas_por_mes[mes_ano] = row['total_empresas']

        return empresas_por_mes

    except Exception as e:
        print(f"Erro ao consultar as empresas: {e}")
        return None
