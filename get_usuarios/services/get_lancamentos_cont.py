from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
import json


from datetime import datetime
from django.http import JsonResponse

def get_lancamentos_manuais(start_date, end_date):
    try:
        # Consultas para cada tipo de dado com agrupamento por mês
        query = f"""
                SELECT codi_emp, codi_usu, EXTRACT(MONTH FROM data_lan) AS mes, COUNT(*) AS total_ocorrencias
                FROM bethadba.ctlancto
                WHERE data_lan BETWEEN '{start_date}' AND '{end_date}'
                AND origem_reg != 0
                GROUP BY codi_emp, codi_usu, mes
                ORDER BY codi_emp, codi_usu, mes
                """

        # Executa as consultas
        result = fetch_data(query)

        # Função para agrupar os dados por empresa e mês
        def agrupar_por_empresa_mes(result):
            dados = {}
            for row in result:
                codi_emp = row['codi_emp']
                codi_usu = row['codi_usu']
                mes = row['mes']
                total_ocorrencias = row['total_ocorrencias']
                
                if codi_emp not in dados:
                    dados[codi_emp] = {}
                
                if codi_usu not in dados[codi_emp]:
                    dados[codi_emp][codi_usu] = {i: 0 for i in range(1, 13)}  # Inicializa meses (1 a 12)
                
                dados[codi_emp][codi_usu][mes] += total_ocorrencias

            return dados

        # Agrupa os dados de saídas, entradas e serviços
        lancamentos_agrupados = agrupar_por_empresa_mes(result)

        # Função para formatar os dados de maneira mais organizada
        def formatar_mes(dados, primeiro_mes, ultimo_mes):
            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            for codi_emp in dados:
                total_empresa = 0  # Variável para armazenar o total de ocorrências por empresa
                for codi_usu in dados[codi_emp]:
                    mes_ocorrencias = {
                        meses[i]: dados[codi_emp][codi_usu][i+1] 
                        for i in range(primeiro_mes-1, ultimo_mes)  # Limita entre o primeiro e o último mês informado
                    }
                    total_ocorrencias = sum(mes_ocorrencias.values())  # Soma todas as ocorrências
                    mes_ocorrencias["total"] = total_ocorrencias  # Adiciona o total de ocorrências
                    dados[codi_emp][codi_usu] = mes_ocorrencias
                    total_empresa += total_ocorrencias  # Soma as ocorrências do usuário para a empresa

                # Adiciona o total geral para a empresa
                dados[codi_emp]["total_geral"] = total_empresa

            return dados

        # Descobre o último mês do período
        ultimo_mes = int(datetime.strptime(end_date, '%Y-%m-%d').strftime('%m'))
        primeiro_mes = int(datetime.strptime(start_date, '%Y-%m-%d').strftime('%m'))

        # Formata os dados para o mês
        lancamentos_formatos = formatar_mes(lancamentos_agrupados, primeiro_mes, ultimo_mes)

        # Retorna a resposta JSON
        return JsonResponse(lancamentos_formatos, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_lancamentos_usuario(start_date, end_date):
    try:
        # Consultando a tabela de saídas e contando as ocorrências
        query = f"""
            SELECT codi_usu, COUNT(*) AS total_ocorrencias
            FROM bethadba.ctlancto
            WHERE data_lan BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY codi_usu
            ORDER BY total_ocorrencias DESC
        """
        result= fetch_data(query)

        # Estruturando o resultado final com as três tabelas separadas
        return JsonResponse(result, safe=False)

    except Exception as e:
        # Retorna um erro caso haja algum problema
        return JsonResponse({"error": str(e)}, status=500)


def get_lancamentos_empresa(start_date, end_date):
    try:
        # Consultas para cada tipo de dado com agrupamento por mês
        query = f"""
        SELECT codi_emp, codi_usu, EXTRACT(MONTH FROM data_lan) AS mes, COUNT(*) AS total_ocorrencias
        FROM bethadba.ctlancto
        WHERE data_lan BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, codi_usu, mes
        ORDER BY codi_emp, codi_usu, mes
        """
        
        # Executa as consultas
        result = fetch_data(query)

        # Função para agrupar os dados por empresa e mês
        def agrupar_por_empresa_mes(result):
            dados = {}
            for row in result:
                codi_emp = row['codi_emp']
                codi_usu = row['codi_usu']
                mes = row['mes']
                total_ocorrencias = row['total_ocorrencias']
                
                if codi_emp not in dados:
                    dados[codi_emp] = {}
                
                if codi_usu not in dados[codi_emp]:
                    dados[codi_emp][codi_usu] = {i: 0 for i in range(1, 13)}  # Inicializa meses (1 a 12)
                
                dados[codi_emp][codi_usu][mes] += total_ocorrencias

            return dados

        # Agrupa os dados de saídas, entradas e serviços
        lancamentos_agrupados = agrupar_por_empresa_mes(result)

        # Função para formatar os dados de maneira mais organizada
        def formatar_mes(dados, primeiro_mes, ultimo_mes):
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            formatted_data = []
            for codi_emp in dados:
                lancamentos = {}
                for codi_usu in dados[codi_emp]:
                    mes_ocorrencias = {
                        meses[i]: dados[codi_emp][codi_usu][i+1] 
                        for i in range(primeiro_mes-1, ultimo_mes)  # Limita entre o primeiro e o último mês informado
                    }
                    total_ocorrencias = sum(mes_ocorrencias.values())  # Soma todas as ocorrências
                    mes_ocorrencias["total"] = total_ocorrencias  # Adiciona o total de ocorrências
                    lancamentos[codi_usu] = mes_ocorrencias
                
                # Adiciona a estrutura de codi_emp com lançamentos
                formatted_data.append({
                    "codi_emp": codi_emp,
                    "dados": lancamentos
                })
            
            return formatted_data

        # Descobre o último mês do período
        ultimo_mes = int(datetime.strptime(end_date, '%Y-%m-%d').strftime('%m'))
        primeiro_mes = int(datetime.strptime(start_date, '%Y-%m-%d').strftime('%m'))

        # Formata os dados para o mês
        lancamentos_formatos = formatar_mes(lancamentos_agrupados, primeiro_mes, ultimo_mes)

        # Retorna a resposta JSON
        return JsonResponse(lancamentos_formatos, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
