from datetime import datetime
import calendar
from odbc_reader.services import fetch_data


def get_novos_mes(start_date, end_date):
    try:
        empresas_por_mes = []

        # Convertendo as datas para datetime
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Consulta 1: Para contar o total de empresas por ano e mês
        query1 = f"""
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

        # Consulta 2: Para pegar todas as empresas
        query2 = f"""
        SELECT 
            nome_emp AS nome_empresa,
            cgce_emp AS cnpj,
            dcad_emp AS data_cadastro,
            stat_emp AS situacao,
            rleg_emp AS responsavel,
            EXTRACT(YEAR FROM dcad_emp) AS ano,
            EXTRACT(MONTH FROM dcad_emp) AS mes
        FROM bethadba.geempre
        WHERE stat_emp = 'A'
        AND dcad_emp <= '{end_date.strftime('%Y-%m-%d')}'  -- Empresas com data de cadastro até a data final
        """

        # Obtém os resultados das duas consultas
        result1 = fetch_data(query1)
        result2 = fetch_data(query2)

        print("Resultado da consulta1 (contagem de empresas):", result1)
        print("Resultado da consulta2 (empresas):", result2)

        # Processa os resultados da consulta 1 (contagem de empresas)
        for row in result1:
            mes_ano = f"{calendar.month_abbr[int(row['mes'])].lower()}/{int(row['ano'])}"
            mes_ref = datetime(row["ano"], int(row["mes"]), 1)

            if start_date <= mes_ref <= end_date:
                empresas_no_mes = []

                # Encontra as empresas que correspondem ao ano e mês da consulta 1
                for empresa in result2:
                    if empresa['ano'] == row['ano'] and empresa['mes'] == row['mes']:
                        empresas_no_mes.append({
                            "nome_empresa": empresa['nome_empresa'],
                            "cnpj": empresa['cnpj'],
                            "data_cadastro": empresa['data_cadastro'],
                            "situacao": empresa['situacao'],
                            "responsavel": empresa['responsavel']
                        })

                # Adiciona os dados do mês com a lista de empresas
                empresas_por_mes.append({
                    "month": mes_ano,
                    "value": row["total_empresas"],
                    "empresas": empresas_no_mes
                })

        return empresas_por_mes

    except Exception as e:
        print(f"Erro ao consultar as empresas: {e}")
        return None
