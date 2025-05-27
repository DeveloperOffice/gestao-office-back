from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime, date
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

def get_faturamento(data_inicial, data_final):
    try:
        query = f"""
            WITH dados_saidas AS (
                SELECT 
                    codi_emp,
                    EXTRACT(MONTH FROM dsai_sai) as mes,
                    EXTRACT(YEAR FROM dsai_sai) as ano,
                    SUM(vcon_sai) as total_saidas
                FROM bethadba.efsaidas
                WHERE dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'
                GROUP BY codi_emp, EXTRACT(MONTH FROM dsai_sai), EXTRACT(YEAR FROM dsai_sai)
            ),
            dados_servicos AS (
                SELECT 
                    codi_emp,
                    EXTRACT(MONTH FROM dser_ser) as mes,
                    EXTRACT(YEAR FROM dser_ser) as ano,
                    SUM(vcon_ser) as total_servicos
                FROM bethadba.efservicos
                WHERE dser_ser BETWEEN '{data_inicial}' AND '{data_final}'
                  AND NOT EXISTS (
                      SELECT 1 FROM bethadba.efsaidas
                      WHERE efsaidas.codi_emp = efservicos.codi_emp
                        AND efsaidas.dsai_sai = efservicos.dser_ser
                  )
                GROUP BY codi_emp, EXTRACT(MONTH FROM dser_ser), EXTRACT(YEAR FROM dser_ser)
            )
            SELECT 
                COALESCE(s.codi_emp, sv.codi_emp) as codi_emp,
                COALESCE(s.mes, sv.mes) as mes,
                COALESCE(s.ano, sv.ano) as ano,
                COALESCE(s.total_saidas, 0) as total_saidas,
                COALESCE(sv.total_servicos, 0) as total_servicos
            FROM dados_saidas s
            FULL OUTER JOIN dados_servicos sv ON s.codi_emp = sv.codi_emp AND s.mes = sv.mes AND s.ano = sv.ano
            ORDER BY codi_emp, ano, mes
        """

 
        dados = fetch_data(query)
        if not dados:
            return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

        meses = {
            1: "jan", 2: "fev", 3: "mar", 4: "abr",
            5: "mai", 6: "jun", 7: "jul", 8: "ago",
            9: "set", 10: "out", 11: "nov", 12: "dez"
        }

        try:
            data_inicial_obj = datetime.strptime(data_inicial, '%Y-%m-%d').date()
            data_final_obj = datetime.strptime(data_final, '%Y-%m-%d').date()
            
            if data_inicial_obj.year == data_final_obj.year and data_inicial_obj.month == data_final_obj.month:
                meses_periodo = {data_inicial_obj.month: meses[data_inicial_obj.month]}
            elif data_inicial_obj.year == data_final_obj.year:
                meses_periodo = {m: nome for m, nome in meses.items() 
                                if data_inicial_obj.month <= m <= data_final_obj.month}
            else:
                meses_periodo = {}
                for m in range(data_inicial_obj.month, 13):
                    meses_periodo[m] = meses[m]
                for m in range(1, data_final_obj.month + 1):
                    meses_periodo[m] = meses[m]
        except ValueError:
            logger.warning("Erro ao processar datas. Usando todos os meses.")
            meses_periodo = meses

        resultado = {}
        
        for item in dados:
            codi_emp = str(item.get("codi_emp", ""))
            mes_num = int(item.get("mes", 0))
            
            if not codi_emp or mes_num not in meses_periodo:
                continue
                
            mes_nome = meses_periodo[mes_num]
            
            if codi_emp not in resultado:
                resultado[codi_emp] = {
                    "Faturamento": {
                        "Saidas": {mes: {"valor": "0", "diferenca": "0%"} for mes in meses_periodo.values()},
                        "servicos": {mes: {"valor": "0", "diferenca": "0%"} for mes in meses_periodo.values()},
                        "Total": {
                            "Total Saidas": "0",
                            "Total servicos": "0"
                        }
                    }
                }
            
            estrutura = resultado[codi_emp]["Faturamento"]
            
            valor_saidas = float(item.get("total_saidas", 0))
            if valor_saidas > 0:
                estrutura["Saidas"][mes_nome]["valor"] = str(valor_saidas)
                
                total_saidas = float(estrutura["Total"]["Total Saidas"])
                estrutura["Total"]["Total Saidas"] = str(total_saidas + valor_saidas)
            
            valor_servicos = float(item.get("total_servicos", 0))
            if valor_servicos > 0:
                estrutura["servicos"][mes_nome]["valor"] = str(valor_servicos)
                
                total_servicos = float(estrutura["Total"]["Total servicos"])
                estrutura["Total"]["Total servicos"] = str(total_servicos + valor_servicos)

        for codi_emp, dados_empresa in resultado.items():
            faturamento = dados_empresa["Faturamento"]
            
            meses_ordenados = sorted(meses_periodo.items(), key=lambda x: x[0])
            
            for i, (mes_num, mes_nome) in enumerate(meses_ordenados):
                if i == 0:
                    faturamento["Saidas"][mes_nome]["diferenca"] = "0%"
                    faturamento["servicos"][mes_nome]["diferenca"] = "0%"
                else:
                    mes_anterior = meses_ordenados[i-1][1]
                    
                    valor_atual = float(faturamento["Saidas"][mes_nome]["valor"])
                    valor_anterior = float(faturamento["Saidas"][mes_anterior]["valor"])
                    
                    if valor_anterior > 0:
                        diferenca = ((valor_atual - valor_anterior) / valor_anterior) * 100
                        faturamento["Saidas"][mes_nome]["diferenca"] = f"{diferenca:.2f}%"
                    else:
                        faturamento["Saidas"][mes_nome]["diferenca"] = "0%"
                    
                    valor_atual = float(faturamento["servicos"][mes_nome]["valor"])
                    valor_anterior = float(faturamento["servicos"][mes_anterior]["valor"])
                    
                    if valor_anterior > 0:
                        diferenca = ((valor_atual - valor_anterior) / valor_anterior) * 100
                        faturamento["servicos"][mes_nome]["diferenca"] = f"{diferenca:.2f}%"
                    else:
                        faturamento["servicos"][mes_nome]["diferenca"] = "0%"

        total_registros = len(dados)
        empresas_encontradas = len(resultado)
        
        logger.info(f"Total de registros: {total_registros}")
        logger.info(f"Empresas encontradas: {empresas_encontradas}")

        dados_formatados = []
        for codi_emp, conteudo in resultado.items():
            dados_formatados.append({
                "codi_emp": codi_emp,
                **conteudo  
            })

        response_data = {
            "dados": dados_formatados,
            "info_processamento": {
                "total_registros": total_registros,
                "empresas_encontradas": empresas_encontradas,
                "meses_periodo": list(meses_periodo.values())
            }
        }

    except Exception as e:
        logger.exception("Erro ao processar faturamento.")
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(response_data, safe=False)
