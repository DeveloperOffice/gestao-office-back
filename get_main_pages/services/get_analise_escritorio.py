from django.http import JsonResponse
from odbc_reader.services import fetch_data
import logging
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

def get_analise_escritorio():
    try:
        current_date = datetime.now()
        previous_month = current_date - timedelta(days=30)
        
        query_escritorios = """
        SELECT DISTINCT
            HRCLIENTE.CODI_EMP AS codigo_escritorio,
            HRCLIENTE.I_CLIENTE_FIXO AS codigo_empresa
        FROM bethadba.HRCLIENTE
        WHERE HRCLIENTE.I_CLIENTE_FIXO IS NOT NULL
        """
        
        query_faturamento = """
        WITH escritorios AS (
            SELECT DISTINCT CODI_EMP 
            FROM bethadba.HRCLIENTE 
            WHERE I_CLIENTE_FIXO IS NOT NULL
        ),
        dados_saidas AS (
            SELECT 
                e.codi_emp,
                SUM(s.vcon_sai) as total_saidas
            FROM escritorios e
            LEFT JOIN bethadba.efsaidas s ON e.codi_emp = s.codi_emp
            GROUP BY e.codi_emp
        ),
        dados_servicos AS (
            SELECT 
                e.codi_emp,
                SUM(sv.vcon_ser) as total_servicos
            FROM escritorios e
            LEFT JOIN bethadba.efservicos sv ON e.codi_emp = sv.codi_emp
            WHERE NOT EXISTS (
                SELECT 1 
                FROM bethadba.efsaidas s
                WHERE s.codi_emp = sv.codi_emp
                  AND s.dsai_sai = sv.dser_ser
            )
            GROUP BY e.codi_emp
        )
        SELECT 
            ds.codi_emp,
            COALESCE(ds.total_saidas, 0) as total_saidas,
            COALESCE(dsv.total_servicos, 0) as total_servicos,
            COALESCE(ds.total_saidas, 0) + COALESCE(dsv.total_servicos, 0) as total_faturamento
        FROM dados_saidas ds
        LEFT JOIN dados_servicos dsv ON ds.codi_emp = dsv.codi_emp
        """

        query_faturamento_variacao = f"""
        WITH escritorios AS (
            SELECT DISTINCT CODI_EMP 
            FROM bethadba.HRCLIENTE 
            WHERE I_CLIENTE_FIXO IS NOT NULL
        ),
        dados_saidas_atual AS (
            SELECT 
                e.codi_emp,
                SUM(s.vcon_sai) as total_saidas
            FROM escritorios e
            LEFT JOIN bethadba.efsaidas s ON e.codi_emp = s.codi_emp
            WHERE s.dsai_sai >= '{previous_month.strftime('%Y-%m-%d')}'
            GROUP BY e.codi_emp
        ),
        dados_servicos_atual AS (
            SELECT 
                e.codi_emp,
                SUM(sv.vcon_ser) as total_servicos
            FROM escritorios e
            LEFT JOIN bethadba.efservicos sv ON e.codi_emp = sv.codi_emp
            WHERE sv.dser_ser >= '{previous_month.strftime('%Y-%m-%d')}'
            AND NOT EXISTS (
                SELECT 1 
                FROM bethadba.efsaidas s
                WHERE s.codi_emp = sv.codi_emp
                  AND s.dsai_sai = sv.dser_ser
            )
            GROUP BY e.codi_emp
        ),
        dados_saidas_anterior AS (
            SELECT 
                e.codi_emp,
                SUM(s.vcon_sai) as total_saidas
            FROM escritorios e
            LEFT JOIN bethadba.efsaidas s ON e.codi_emp = s.codi_emp
            WHERE s.dsai_sai < '{previous_month.strftime('%Y-%m-%d')}'
            AND s.dsai_sai >= '{previous_month.strftime('%Y-%m-%d')}'
            GROUP BY e.codi_emp
        ),
        dados_servicos_anterior AS (
            SELECT 
                e.codi_emp,
                SUM(sv.vcon_ser) as total_servicos
            FROM escritorios e
            LEFT JOIN bethadba.efservicos sv ON e.codi_emp = sv.codi_emp
            WHERE sv.dser_ser < '{previous_month.strftime('%Y-%m-%d')}'
            AND sv.dser_ser >= '{previous_month.strftime('%Y-%m-%d')}'
            AND NOT EXISTS (
                SELECT 1 
                FROM bethadba.efsaidas s
                WHERE s.codi_emp = sv.codi_emp
                  AND s.dsai_sai = sv.dser_ser
            )
            GROUP BY e.codi_emp
        )
        SELECT 
            COALESCE(dsa.codi_emp, dsv.codi_emp) as codi_emp,
            COALESCE(dsa.total_saidas, 0) + COALESCE(dsv.total_servicos, 0) as faturamento_atual,
            COALESCE(dsaa.total_saidas, 0) + COALESCE(dsva.total_servicos, 0) as faturamento_anterior
        FROM dados_saidas_atual dsa
        FULL OUTER JOIN dados_servicos_atual dsv ON dsa.codi_emp = dsv.codi_emp
        FULL OUTER JOIN dados_saidas_anterior dsaa ON dsa.codi_emp = dsaa.codi_emp
        FULL OUTER JOIN dados_servicos_anterior dsva ON dsa.codi_emp = dsva.codi_emp
        """

        query_atividades = """
        SELECT 
            codi_emp,
            SUM(
                (HOUR(tfim_log) * 3600 + MINUTE(tfim_log) * 60 + SECOND(tfim_log)) -
                (HOUR(tini_log) * 3600 + MINUTE(tini_log) * 60 + SECOND(tini_log))
            ) as tempo_total_segundos
        FROM bethadba.geloguser
        GROUP BY codi_emp
        """

        query_lancamentos = """
        SELECT 
            codi_emp,
            COUNT(*) as total_lancamentos
        FROM bethadba.ctlancto
        GROUP BY codi_emp
        """

        query_lancamentos_manuais = """
        SELECT 
            codi_emp,
            COUNT(*) as total_lancamentos_manuais
        FROM bethadba.ctlancto
        WHERE origem_reg != 0
        GROUP BY codi_emp
        """

        query_notas_fiscais = """
        SELECT 
            codi_emp,
            COUNT(*) as total_notas_fiscais
        FROM bethadba.efsaidas
        GROUP BY codi_emp
        """

        query_notas_fiscais_entrada = """
        SELECT 
            codi_emp,
            COUNT(*) as total_notas_fiscais_entrada
        FROM bethadba.efentradas
        GROUP BY codi_emp
        """

        query_vinculos_ativos = """
        SELECT 
            e.codi_emp,
            COUNT(*) as total_vinculos_ativos
        FROM bethadba.foempregados e
        LEFT JOIN bethadba.forescisoes r 
            ON e.codi_emp = r.codi_emp 
            AND e.i_empregados = r.i_empregados
        WHERE r.demissao IS NULL
        GROUP BY e.codi_emp
        """
        
        result_escritorios = fetch_data(query_escritorios)
        result_faturamento = fetch_data(query_faturamento)
        result_faturamento_variacao = fetch_data(query_faturamento_variacao)
        result_atividades = fetch_data(query_atividades)
        result_lancamentos = fetch_data(query_lancamentos)
        result_lancamentos_manuais = fetch_data(query_lancamentos_manuais)
        result_notas_fiscais = fetch_data(query_notas_fiscais)
        result_notas_fiscais_entrada = fetch_data(query_notas_fiscais_entrada)
        result_vinculos_ativos = fetch_data(query_vinculos_ativos)
        
        faturamento_por_empresa = {
            str(item['codi_emp']): float(item['total_faturamento'] or 0)
            for item in result_faturamento
        }

        variacao_por_empresa = {}
        for item in result_faturamento_variacao:
            codi_emp = str(item['codi_emp'])
            faturamento_atual = float(item['faturamento_atual'] or 0)
            faturamento_anterior = float(item['faturamento_anterior'] or 0)
            
            if faturamento_anterior > 0:
                variacao = ((faturamento_atual - faturamento_anterior) / faturamento_anterior) * 100
            else:
                variacao = 0
                
            variacao_por_empresa[codi_emp] = variacao

        tempo_por_empresa = {
            str(item['codi_emp']): int(item['tempo_total_segundos'] or 0)
            for item in result_atividades
        }

        lancamentos_por_empresa = {
            str(item['codi_emp']): int(item['total_lancamentos'] or 0)
            for item in result_lancamentos
        }

        lancamentos_manuais_por_empresa = {
            str(item['codi_emp']): int(item['total_lancamentos_manuais'] or 0)
            for item in result_lancamentos_manuais
        }

        notas_fiscais_por_empresa = {
            str(item['codi_emp']): int(item['total_notas_fiscais'] or 0)
            for item in result_notas_fiscais
        }

        notas_fiscais_entrada_por_empresa = {
            str(item['codi_emp']): int(item['total_notas_fiscais_entrada'] or 0)
            for item in result_notas_fiscais_entrada
        }

        vinculos_ativos_por_empresa = {
            str(item['codi_emp']): int(item['total_vinculos_ativos'] or 0)
            for item in result_vinculos_ativos
        }
        
        escritorios_dict = {}
        
        for item in result_escritorios:
            codigo_escritorio = item['codigo_escritorio']
            codigo_empresa = item['codigo_empresa']
            
            if codigo_escritorio not in escritorios_dict:
                escritorios_dict[codigo_escritorio] = {
                    'id_escritorio': codigo_escritorio,
                    'total_empresas': 0,
                    'faturamento': 0,
                    'tempo_ativo_sistema': 0,
                    'variacao_faturamento': 0,
                    'empresas': []
                }
            
            empresa_info = {
                'id': codigo_empresa,
                'lancamentos': lancamentos_por_empresa.get(str(codigo_empresa), 0),
                'lancamentos_manuais': lancamentos_manuais_por_empresa.get(str(codigo_empresa), 0),
                'notas_fiscais_emitidas': notas_fiscais_por_empresa.get(str(codigo_empresa), 0),
                'notas_fiscais_movimentadas': (
                    notas_fiscais_por_empresa.get(str(codigo_empresa), 0) + 
                    notas_fiscais_entrada_por_empresa.get(str(codigo_empresa), 0)
                ),
                'vinculo_folha_ativo': vinculos_ativos_por_empresa.get(str(codigo_empresa), 0)
            }
            escritorios_dict[codigo_escritorio]['empresas'].append(empresa_info)
            escritorios_dict[codigo_escritorio]['total_empresas'] = len(escritorios_dict[codigo_escritorio]['empresas'])
            
            faturamento_empresa = faturamento_por_empresa.get(str(codigo_empresa), 0)
            escritorios_dict[codigo_escritorio]['faturamento'] += faturamento_empresa

            tempo_empresa = tempo_por_empresa.get(str(codigo_empresa), 0)
            escritorios_dict[codigo_escritorio]['tempo_ativo_sistema'] += tempo_empresa

            variacao_empresa = variacao_por_empresa.get(str(codigo_empresa), 0)
            escritorios_dict[codigo_escritorio]['variacao_faturamento'] = variacao_empresa
        
        resultado_final = {
            "escritorios": list(escritorios_dict.values())
        }
        
        return resultado_final

    except Exception as e:
        logger.error(f"Error in get_analise_escritorio: {str(e)}")
        return {"error": str(e)}