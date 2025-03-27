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

        # Obter os códigos de imposto da empresa
        impostos_da_empresa = [imposto for imposto in impostos["Impostos"] if imposto.get("codi_emp") == codigo]

        # Se a empresa não tem impostos
        if not impostos_da_empresa:
            empresa["regime_tributario"] = "Sem Impostos"
            empresas_validas.append(empresa)
            continue

        # Contadores de impostos
        contagem_simples_nacional = 0
        contagem_lucro_real = 0
        contagem_lucro_presumido = 0
        encontrou_44 = False
        encontrou_7 = False

        for imposto in impostos_da_empresa:
            codi_imp = imposto.get("codi_imp")

            # Se o código 44 for encontrado, classifica automaticamente como Simples Nacional
            if codi_imp == 44:
                encontrou_44 = True
                contagem_simples_nacional += 1
                continue 

            # Se o código 7 for encontrado, classifica automaticamente como Lucro Presumido
            if codi_imp == 7:
                encontrou_7 = True
                contagem_lucro_presumido += 1
                continue  

            # Contagem dos demais impostos
            if codi_imp in [10, 64]:
                contagem_simples_nacional += 1
            elif codi_imp in [17, 106, 140, 19, 107, 134, 141]:
                contagem_lucro_real += 1
            elif codi_imp in [4, 108, 138, 5, 109, 139]:
                contagem_lucro_presumido += 1

        # Se encontrou o código 44 ou 7, prioridade para esses regimes
        if encontrou_44:
            regime_tributario = "Simples Nacional"
        elif encontrou_7:
            regime_tributario = "Lucro Presumido"
        else:
            # Determinar o regime com base na quantidade predominante
            if contagem_simples_nacional > contagem_lucro_real and contagem_simples_nacional > contagem_lucro_presumido:
                regime_tributario = "Simples Nacional"
            elif contagem_lucro_real > contagem_simples_nacional and contagem_lucro_real > contagem_lucro_presumido:
                regime_tributario = "LUCRO REAL"
            else:
                regime_tributario = "Lucro Presumido"

        # Adicionar o regime tributário à empresa
        empresa["regime_tributario"] = regime_tributario
        empresas_validas.append(empresa)
    
    return {"Empresas": empresas_validas}
