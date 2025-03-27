from get_empresas.services.get_client_data import *
import json

def integrate_data():
    empresas = json.loads(get_empresa().content)
    clientes = json.loads(get_cliente().content)
    impostos = json.loads(get_imposto().content)

    empresas_validas = []

    # Agrupar os escritórios por código da empresa
    for empresa in empresas["Empresas"]:
        codigo = empresa.get("codigo_empresa")
        escritorios = []

        # Procurar todos os escritórios para essa empresa
        for escritorio in clientes["Clientes"]:
            if escritorio.get("I_CLIENTE_FIXO") == codigo:
                # Adicionar tanto o código do escritório quanto o I_CLIENTE
                escritorios.append({
                    "codigo_escritorio": escritorio.get("CODI_EMP"),
                    "id_cliente_contrato": escritorio.get("I_CLIENTE")
                })

        # Se encontrou escritórios, adicionar à empresa
        if escritorios:
            empresa["escritorios"] = escritorios
            empresas_validas.append(empresa)
        # Se não encontrar, não adiciona à lista final
    for empresa in empresas_validas:
        codigo = empresa.get("codigo_empresa")
        
    
    return {"Empresas": empresas_validas}
