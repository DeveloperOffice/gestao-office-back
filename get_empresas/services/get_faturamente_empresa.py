from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime, date
import logging

# Configurar logger
logger = logging.getLogger(__name__)

def get_faturamento(data_inicial, data_final):
    try:
        # 1. Saídas com possível serviço (ou NULL se não tiver)
        query_saida = f"""
            SELECT
                efsaidas.codi_emp,
                efsaidas.dsai_sai,
                efsaidas.vcon_sai,
                efsaidas.vexc_sai,
                efservicos.vcon_ser,
                efsaidas.cancelada_sai
            FROM bethadba.efsaidas
            LEFT JOIN bethadba.efservicos
              ON efsaidas.codi_emp = efservicos.codi_emp
             AND efsaidas.dsai_sai = efservicos.dser_ser
            WHERE efsaidas.dsai_sai BETWEEN '{data_inicial}' AND '{data_final}'
        """

        # 2. Serviços que não têm nenhuma nota de saída correspondente
        query_servico = f"""
            SELECT
                efservicos.codi_emp,
                efservicos.dser_ser,
                NULL AS vcon_sai,
                NULL AS vexc_sai,
                efservicos.vcon_ser,
                efservicos.cancelada_ser,
                efservicos.codi_acu
            FROM bethadba.efservicos
            WHERE efservicos.dser_ser BETWEEN '{data_inicial}' AND '{data_final}'
              AND NOT EXISTS (
                  SELECT 1
                  FROM bethadba.efsaidas
                  WHERE efsaidas.codi_emp = efservicos.codi_emp
                    AND efsaidas.dsai_sai = efservicos.dser_ser
              )
        """

        dados_saida = fetch_data(query_saida)
        dados_servico = fetch_data(query_servico)

        # Log para verificar quantos registros foram encontrados
        logger.info(f"Registros de saída encontrados: {len(dados_saida) if dados_saida else 0}")
        logger.info(f"Registros de serviço encontrados: {len(dados_servico) if dados_servico else 0}")

        resultado_completo = (dados_saida or []) + (dados_servico or [])
        logger.info(f"Total de registros a processar: {len(resultado_completo)}")

        if not resultado_completo:
            return JsonResponse({"message": "Nenhum dado encontrado"}, status=404)

        # Criar estrutura de dados para o resultado
        resultado = {}
        
        # Mapeamento de números de mês para nomes abreviados
        meses = {
            1: "jan", 2: "fev", 3: "mar", 4: "abr", 
            5: "mai", 6: "jun", 7: "jul", 8: "ago", 
            9: "set", 10: "out", 11: "nov", 12: "dez"
        }
        
        # Determinar quais meses estão no período solicitado
        try:
            data_inicial_obj = datetime.strptime(data_inicial, '%Y-%m-%d').date()
            data_final_obj = datetime.strptime(data_final, '%Y-%m-%d').date()
            
            # Se as datas são do mesmo ano e mês
            if data_inicial_obj.year == data_final_obj.year and data_inicial_obj.month == data_final_obj.month:
                meses_periodo = {data_inicial_obj.month: meses[data_inicial_obj.month]}
            # Se as datas são do mesmo ano mas meses diferentes
            elif data_inicial_obj.year == data_final_obj.year:
                meses_periodo = {mes: nome for mes, nome in meses.items() 
                                if data_inicial_obj.month <= mes <= data_final_obj.month}
            # Se as datas são de anos diferentes
            else:
                # Para o ano inicial, incluir meses a partir do mês inicial
                meses_periodo = {mes: nome for mes, nome in meses.items() 
                                if mes >= data_inicial_obj.month}
                # Para o ano final, incluir meses até o mês final
                meses_periodo.update({mes: nome for mes, nome in meses.items() 
                                     if mes <= data_final_obj.month})
        except ValueError:
            # Se houver erro na conversão das datas, usar todos os meses
            logger.warning(f"Erro ao converter datas: {data_inicial}, {data_final}. Usando todos os meses.")
            meses_periodo = meses
        
        # Contadores para verificação
        contador_saidas_processadas = 0
        contador_servicos_processados = 0
        contador_erros_data = 0
        
        # Processar dados de saída
        for item in dados_saida:
            codi_emp = str(item.get('codi_emp', ''))
            if not codi_emp:
                continue
                
            # Inicializar estrutura para a empresa se não existir
            if codi_emp not in resultado:
                resultado[codi_emp] = {
                    "Faturamento": {
                        "Saidas": {mes: "0" for mes in meses_periodo.values()},
                        "servicos": {mes: "0" for mes in meses_periodo.values()}
                    }
                }
            
            # Obter data e mês
            data = item.get('dsai_sai')
            if not data:
                continue
                
            try:
                # Verificar se data já é um objeto date
                if isinstance(data, date):
                    data_obj = data
                else:
                    # Tentar converter string para date
                    data_obj = datetime.strptime(data, '%Y-%m-%d').date()
                
                # Verificar se o mês está no período solicitado
                if data_obj.month not in meses_periodo:
                    continue
                    
                mes = meses_periodo[data_obj.month]
            except (ValueError, KeyError, AttributeError) as e:
                logger.error(f"Erro ao processar data: {e}, valor: {data}, tipo: {type(data)}")
                contador_erros_data += 1
                continue
            
            # Adicionar valor de saída
            vcon_sai = item.get('vcon_sai')
            if vcon_sai is not None:
                valor_atual = float(resultado[codi_emp]["Faturamento"]["Saidas"][mes])
                valor_atual += float(vcon_sai)
                resultado[codi_emp]["Faturamento"]["Saidas"][mes] = str(valor_atual)
            
            # Adicionar valor de serviço
            vcon_ser = item.get('vcon_ser')
            if vcon_ser is not None:
                valor_atual = float(resultado[codi_emp]["Faturamento"]["servicos"][mes])
                valor_atual += float(vcon_ser)
                resultado[codi_emp]["Faturamento"]["servicos"][mes] = str(valor_atual)
            
            contador_saidas_processadas += 1
        
        # Processar dados de serviço
        for item in dados_servico:
            codi_emp = str(item.get('codi_emp', ''))
            if not codi_emp:
                continue
                
            # Inicializar estrutura para a empresa se não existir
            if codi_emp not in resultado:
                resultado[codi_emp] = {
                    "Faturamento": {
                        "Saidas": {mes: "0" for mes in meses_periodo.values()},
                        "servicos": {mes: "0" for mes in meses_periodo.values()}
                    }
                }
            
            # Obter data e mês
            data = item.get('dser_ser')
            if not data:
                continue
                
            try:
                # Verificar se data já é um objeto date
                if isinstance(data, date):
                    data_obj = data
                else:
                    # Tentar converter string para date
                    data_obj = datetime.strptime(data, '%Y-%m-%d').date()
                
                # Verificar se o mês está no período solicitado
                if data_obj.month not in meses_periodo:
                    continue
                    
                mes = meses_periodo[data_obj.month]
            except (ValueError, KeyError, AttributeError) as e:
                logger.error(f"Erro ao processar data: {e}, valor: {data}, tipo: {type(data)}")
                contador_erros_data += 1
                continue
            
            # Adicionar valor de serviço
            vcon_ser = item.get('vcon_ser')
            if vcon_ser is not None:
                valor_atual = float(resultado[codi_emp]["Faturamento"]["servicos"][mes])
                valor_atual += float(vcon_ser)
                resultado[codi_emp]["Faturamento"]["servicos"][mes] = str(valor_atual)
            
            contador_servicos_processados += 1
        
        # Log para verificar o processamento
        logger.info(f"Saídas processadas: {contador_saidas_processadas}")
        logger.info(f"Serviços processados: {contador_servicos_processados}")
        logger.info(f"Erros de data: {contador_erros_data}")
        logger.info(f"Empresas encontradas: {len(resultado)}")
        
        # Adicionar informações de processamento à resposta
        info_processamento = {
            "total_registros": len(resultado_completo),
            "saidas_processadas": contador_saidas_processadas,
            "servicos_processados": contador_servicos_processados,
            "erros_data": contador_erros_data,
            "empresas_encontradas": len(resultado),
            "meses_periodo": list(meses_periodo.values())
        }
        
        response_data = {
            "dados": resultado,
            "info_processamento": info_processamento
        }

    except Exception as e:
        logger.error(f"Erro ao processar faturamento: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(response_data, safe=False)
