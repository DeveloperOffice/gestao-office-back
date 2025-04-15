from datetime import datetime
import json
from get_empresas.services.get_client_data import *
from get_empresas.services.get_regime_tributario import get_regime, get_regime_secundario

def integrate_data():
    # Integrando todos os dados para formar a lista de clientes
    empresas = json.loads(get_empresa().content)
    clientes = json.loads(get_cliente().content)
    regimes = get_regime()

    # Lista que guardará todas as empresas válidas
    empresas_validas = []

    # Lista que guardará todas as empresas que não se enquadram em um regime
    empresas_sem_regime = []

    # Passo 1: Pré-processar regimes e manter só o mais recente por CODI_EMP
    regimes_mais_recentes = {}
    regimes_mapping = {
                        1: 'Lucro Real',
                        2: 'Micro Empresa',
                        3: 'Estimativa',
                        4: 'Empresa Pequeno Porte',
                        5: 'Lucro Presumido',
                        6: 'Regime Especial de Tributação',
                        7: 'Lucro Arbitrado',
                        8: 'Imune do IRPJ',
                        9: 'Isenta de IRPJ'
                    }

    for regime in regimes:
        codi_emp = regime['CODI_EMP']
        vigencia = regime['VIGENCIA_PAR']  # já é datetime.date ou datetime.datetime

        if codi_emp not in regimes_mais_recentes:
            regimes_mais_recentes[codi_emp] = regime
        else:
            vigencia_atual = regimes_mais_recentes[codi_emp]['VIGENCIA_PAR']
            if vigencia > vigencia_atual:
                regimes_mais_recentes[codi_emp] = regime

    # Passo 2: Integrar dados
    for empresa in empresas["Empresas"]:
        codigo = empresa.get("codigo_empresa")
        escritorios = []

        # Passo 3: Adicionar o nome do escritório (empresa) correspondente
        for escritorio in clientes["Clientes"]:
            if escritorio.get("I_CLIENTE_FIXO") == codigo:
                nome_escritorio = next(
                    (emp["nome_empresa"] for emp in empresas["Empresas"] if emp["codigo_empresa"] == escritorio.get("CODI_EMP")),
                    None
                )
                escritorios.append({
                    "codigo_escritorio": escritorio.get("CODI_EMP"),
                    "id_cliente_contrato": escritorio.get("I_CLIENTE"),
                    "nome_escritorio": nome_escritorio  # Adiciona o nome do escritório
                })

        if escritorios:
            empresa["escritorios"] = escritorios

        # Regime tributário mais recente
        if codigo in regimes_mais_recentes:
            if regimes_mais_recentes[codigo]["SIMPLESN_OPTANTE_PAR"] == "S":
                empresa["regime_tributario"] = "Simples Nacional"
            else:    
                regime_formatado = regimes_mapping[regimes_mais_recentes[codigo]["RFED_PAR"]]
                empresa["regime_tributario"] = regime_formatado
                
                if regime_formatado in ['Estimativa', 
                                        'Empresa Pequeno Porte', 
                                        'Micro Empresa', 
                                        'Regime Especial de Tributação', 
                                        'Lucro Arbitrado']:
                    empresas_sem_regime.append(codigo)
        else:
            empresa["regime_tributario"] = 'N/D'
            empresas_sem_regime.append(codigo)

        empresas_validas.append(empresa)

    empresas_por_codigo = {item['codigo_empresa']: item for item in empresas_validas}
    lista_regimes_segundarios = get_regime_secundario(empresas_sem_regime)

    for i in lista_regimes_segundarios:
        # Alterar diretamente a empresa do código atual
        if i["codi_emp"] in empresas_por_codigo:

            # Doméstica
            if i["GERAR_ESOCIAL_DOMESTICO"] == 1 or i["CLASSIFICACAO_TRIBUTARIA"] == 12:
                empresas_por_codigo[i["codi_emp"]]['regime_tributario'] = 'Doméstica'

            # Produtor Rural    
            elif i["PRODUTOR_RURAL"] == 1 or i["CLASSIFICACAO_TRIBUTARIA"] == 6:
                empresas_por_codigo[i["codi_emp"]]['regime_tributario'] = 'Produtor Rural'

            # MEI    
            elif i["CLASSIFICACAO_TRIBUTARIA"] == 4:
                empresas_por_codigo[i["codi_emp"]]['regime_tributario'] = 'MEI'

    return {"Empresas": empresas_validas}
