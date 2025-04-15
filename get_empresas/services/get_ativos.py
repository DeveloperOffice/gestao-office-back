from datetime import datetime
import calendar
from odbc_reader.services import fetch_data

def get_ativos_mes(start_date, end_date):
    try:
        # Inicializa a lista para armazenar os dados dos meses
        empresas_por_mes = []
        total_empresas_acumulado = 0

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

        # Processa os resultados e acumula as empresas mês a mês dentro do intervalo
        for row in result:
            mes_ano = f"{calendar.month_abbr[int(row['mes'])].lower()}/{int(row['ano'])}"

            # Acumula as empresas de cada mês até o final do mês de referência
            total_empresas_acumulado += row['total_empresas']
            
            # Verifica se o mês está dentro do intervalo start_date e end_date
            mes_ref = datetime(row['ano'], int(row['mes']), 1)
            if start_date <= mes_ref <= end_date:
                empresas_por_mes.append({
                    "month": mes_ano,
                    "value": total_empresas_acumulado
                })

        return empresas_por_mes

    except Exception as e:
        print(f"Erro ao consultar as empresas: {e}")
        return None
