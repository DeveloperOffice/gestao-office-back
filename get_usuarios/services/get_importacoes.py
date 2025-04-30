from django.http import JsonResponse
from odbc_reader.services import fetch_data
import json

def get_importacoes_usuario(start_date, end_date):
    try:
        meses_abrev = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun',
                       'jul', 'ago', 'set', 'out', 'nov', 'dez']

        def processa(query, campo_data):
            sql = f"""
                SELECT codi_usu, EXTRACT(MONTH FROM {campo_data}) AS mes, COUNT(*) AS total_ocorrencias
                FROM {query}
                WHERE {campo_data} BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY codi_usu, mes
                ORDER BY codi_usu, mes
            """
            result = fetch_data(sql)
            dados = {}
            for row in result:
                codi_usu = row['codi_usu']
                mes = row['mes']
                total = row['total_ocorrencias']
                if codi_usu not in dados:
                    dados[codi_usu] = {i: 0 for i in range(1, 13)}
                dados[codi_usu][mes] += total
            return dados

        # Consulta agrupada por mês para cada tabela
        saidas = processa("bethadba.efsaidas", "dsai_sai")
        entradas = processa("bethadba.efentradas", "dent_ent")
        servicos = processa("bethadba.efservicos", "dser_ser")

        def formatar(dados):
            formatado = []
            for codi_usu, meses_dict in dados.items():
                item = {"codi_usu": codi_usu}
                for i in range(1, 13):
                    item[meses_abrev[i - 1]] = meses_dict[i]
                formatado.append(item)
            return formatado

        # Retorna os dados formatados
        return JsonResponse({
            "saidas": formatar(saidas),
            "entradas": formatar(entradas),
            "servicos": formatar(servicos)
        }, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime


def get_importacoes_empresa(start_date, end_date):
    try:
        # Consultas para cada tipo de dado com agrupamento por mês
        query_saida = f"""
        SELECT codi_emp, codi_usu, EXTRACT(MONTH FROM dsai_sai) AS mes, COUNT(*) AS total_ocorrencias
        FROM bethadba.efsaidas
        WHERE dsai_sai BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, codi_usu, mes
        ORDER BY codi_emp, codi_usu, mes
        """
        
        query_entrada = f"""
        SELECT codi_emp, codi_usu, EXTRACT(MONTH FROM dent_ent) AS mes, COUNT(*) AS total_ocorrencias
        FROM bethadba.efentradas
        WHERE dent_ent BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, codi_usu, mes
        ORDER BY codi_emp, codi_usu, mes
        """
        
        query_servicos = f"""
        SELECT codi_emp, codi_usu, EXTRACT(MONTH FROM dser_ser) AS mes, COUNT(*) AS total_ocorrencias
        FROM bethadba.efservicos
        WHERE dser_ser BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, codi_usu, mes
        ORDER BY codi_emp, codi_usu, mes
        """

        # Executa as consultas
        result_saida = fetch_data(query_saida)
        result_entrada = fetch_data(query_entrada)
        result_servicos = fetch_data(query_servicos)
        
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
        saídas_agrupadas = agrupar_por_empresa_mes(result_saida)
        entradas_agrupadas = agrupar_por_empresa_mes(result_entrada)
        servicos_agrupados = agrupar_por_empresa_mes(result_servicos)

        # Função para formatar os dados de maneira mais organizada
        def formatar_mes(dados, primeiro_mes, ultimo_mes):
            meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
            for codi_emp in dados:
                for codi_usu in dados[codi_emp]:
                    mes_ocorrencias = {
                        meses[i]: dados[codi_emp][codi_usu][i+1] 
                        for i in range(primeiro_mes-1, ultimo_mes)  # Limita entre o primeiro e o último mês informado
                    }
                    total_ocorrencias = sum(mes_ocorrencias.values())  # Soma todas as ocorrências
                    mes_ocorrencias["total"] = total_ocorrencias  # Adiciona o total de ocorrências
                    dados[codi_emp][codi_usu] = mes_ocorrencias
            return dados

        # Descobre o último mês do período
        ultimo_mes = int(datetime.strptime(end_date, '%Y-%m-%d').strftime('%m'))
        primeiro_mes = int(datetime.strptime(start_date, '%Y-%m-%d').strftime('%m'))

        # Formata os dados para o mês
        saídas_formatadas = formatar_mes(saídas_agrupadas, primeiro_mes, ultimo_mes)
        entradas_formatadas = formatar_mes(entradas_agrupadas, primeiro_mes, ultimo_mes)
        servicos_formatados = formatar_mes(servicos_agrupados, primeiro_mes, ultimo_mes)

        # Reorganiza a estrutura em uma lista de objetos
        importacoes = []
        for codi_emp in saídas_formatadas:
            # Calcular as somas totais para saídas, entradas, servicos e geral
            total_saidas = sum(sum(v.values()) for v in saídas_formatadas[codi_emp].values())
            total_entradas = sum(sum(v.values()) for v in entradas_formatadas.get(codi_emp, {}).values())
            total_servicos = sum(sum(v.values()) for v in servicos_formatados.get(codi_emp, {}).values())
            total_geral = total_saidas + total_entradas + total_servicos

            importacoes.append({
                "codi_emp": codi_emp,
                "dados": {
                    "saidas": saídas_formatadas[codi_emp],
                    "entradas": entradas_formatadas.get(codi_emp, {}),
                    "servicos": servicos_formatados.get(codi_emp, {}),
                    "total_saidas": total_saidas,
                    "total_entradas": total_entradas,
                    "total_servicos": total_servicos,
                    "total_geral": total_geral
                }
            })

        return JsonResponse(importacoes, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

