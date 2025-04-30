from django.http import JsonResponse
from odbc_reader.services import fetch_data
from get_empresas.services.get_client_data import get_empresa
import json
from datetime import datetime

#Função para formatar o formato do Horário em segundos
def format_log_time(start_log, end_log):
    formato = "%H:%M:%S"
    
    inicio = datetime.strptime(start_log, formato)
    fim = datetime.strptime(end_log, formato)

    diferenca_em_segundos = int((fim - inicio).total_seconds())

    return diferenca_em_segundos

def get_lista_usuario():
    try:
        query = 'SELECT i_usuario, i_confusuario, user_id, usa_modulo_web, usuario_modulo_web, senha_modulo_web, SITUACAO, NOME, USA_ONVIO, LOGIN_ONVIO_VALIDO, USUARIO_ONVIO, SENHA_ONVIO FROM bethadba.usConfUsuario'
        result = fetch_data(query)
        
    except Exception as e:
        
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(result, safe=False)

def get_atividades_usuario(start_date, end_date):
    try:
        query = f"""
        SELECT * FROM bethadba.geloguser 
        WHERE data_log BETWEEN '{start_date}' AND '{end_date}'
        """
        result = fetch_data(query)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(result, safe=False)


def get_atividades_usuario_cliente(start_date, end_date):
    try:
        atividades = json.loads(get_atividades_usuario(start_date, end_date).content)
        empresas = json.loads(get_empresa().content)

        meses_abrev = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun',
                       'jul', 'ago', 'set', 'out', 'nov', 'dez']

        resultado = {}
        meses_encontrados = set()

        for atividade in atividades:
            usuario = atividade['usua_log']
            empresa = atividade['codi_emp']
            tempo_gasto = format_log_time(atividade['tini_log'], atividade['tfim_log'])
            mes = int(datetime.strptime(atividade['data_log'], "%Y-%m-%d").strftime('%m'))

            meses_encontrados.add(mes)

            if empresa not in resultado:
                resultado[empresa] = {}

            if usuario not in resultado[empresa]:
                resultado[empresa][usuario] = {}

            if mes not in resultado[empresa][usuario]:
                resultado[empresa][usuario][mes] = 0

            resultado[empresa][usuario][mes] += tempo_gasto

        # Ordena os meses encontrados
        meses_ordenados = sorted(list(meses_encontrados))

        agrupado = []

        for empresa, usuarios in resultado.items():
            empresa_dados = {
                "codi_emp": empresa,
                "dados": [],
                "tempo_gasto_total": 0
            }

            for usuario, meses_dict in usuarios.items():
                usuario_data = {"usuario": usuario}
                total_usuario = 0

                for i in meses_ordenados:
                    tempo = meses_dict.get(i, 0)
                    usuario_data[meses_abrev[i - 1]] = tempo
                    total_usuario += tempo

                usuario_data["total"] = total_usuario
                empresa_dados["dados"].append(usuario_data)
                empresa_dados["tempo_gasto_total"] += total_usuario

            for empresa_info in empresas['Empresas']:
                if empresa_info['codigo_empresa'] == empresa:
                    empresa_dados["nome_empresa"] = empresa_info['nome_empresa']
                    break

            empresa_dados = {
                "nome_empresa": empresa_dados.get("nome_empresa", ""),
                **empresa_dados
            }

            agrupado.append(empresa_dados)

        return JsonResponse({"Atividades": agrupado}, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_atividades_usuario_modulo(start_date, end_date):
    
    module_mapping = {  
                        1: 'Contabil',
                        3: 'Honorarios',
                        4: 'Patrimonio',
                        5: 'Escrita Fiscal',
                        6: 'Lalur',
                        7: 'Atualizar',
                        8: 'Protocolos',
                        9: 'Administrar',
                        12: 'Folha',
                        13: 'Ponto Eletronico',
                        14: 'Auditoria',
                        15: 'Registro'
                        }
    
    total = json.loads(get_atividades_usuario(start_date, end_date).content)
    resultado = {}
    
    
    for atividade in total:
        usuario = atividade['usua_log']
        modulo = atividade['sist_log']
        modulo_formatado = module_mapping[modulo]
        tempo_gasto = format_log_time(atividade['tini_log'], atividade['tfim_log'])
        
        if modulo_formatado not in resultado:
            resultado[modulo_formatado] = {}
        
        if usuario not in resultado[modulo_formatado]:
            resultado[modulo_formatado][usuario] = 0 
               
        resultado[modulo_formatado][usuario] += tempo_gasto 
        
    
           

    return JsonResponse(resultado, safe=False)
