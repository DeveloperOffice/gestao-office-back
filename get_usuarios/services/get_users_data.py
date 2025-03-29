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
    total = json.loads(get_atividades_usuario(start_date, end_date).content)
    empresas = json.loads(get_empresa().content)
    
    resultado = {}
    
    for atividade in total:
        usuario = atividade['usua_log']
        empresa = atividade['codi_emp']
        tempo_gasto = format_log_time(atividade['tini_log'], atividade['tfim_log'])
        
        if empresa not in resultado:
            resultado[empresa] = {}
        
        if usuario not in resultado[empresa]:
            resultado[empresa][usuario] = 0
        
        resultado[empresa][usuario] += tempo_gasto

    
    agrupado = {}
    
    for empresa, usuarios in resultado.items():
        agrupado[empresa] = {
            "nome_empresa": "", 
            "usuarios": []
        }
        for usuario, tempo in usuarios.items():
            agrupado[empresa]['usuarios'].append({
                "usuario": usuario,
                "tempo_gasto": tempo
            })
            
    for empresa in empresas['Empresas']:
        id_empresa = empresa['codigo_empresa']
        nome_empresa = empresa['nome_empresa']
        
        if id_empresa in agrupado:
            agrupado[id_empresa]['nome_empresa'] = nome_empresa

            
                

    return JsonResponse(agrupado, safe=False)

    
        
        