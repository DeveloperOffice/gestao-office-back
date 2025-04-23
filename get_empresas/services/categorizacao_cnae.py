def categoria_por_cnae(cnae):
    if not cnae:
        return "Desconhecido"
    try:
        prefixo = int(str(cnae).replace("-", "").replace("/", "")[:2])
        if prefixo in range(1, 10):
            return "Agropecuária"
        elif prefixo in range(10, 34):
            return "Indústria"
        elif prefixo == 35:
            return "Energia"
        elif prefixo in range(36, 40):
            return "Saneamento e Resíduos"
        elif prefixo in range(41, 44):
            return "Construção"
        elif prefixo in range(45, 48):
            return "Comércio"
        elif prefixo in range(49, 54):
            return "Transporte e Logística"
        elif prefixo in range(55, 57):
            return "Hospedagem e Alimentação"
        elif prefixo in range(58, 64):
            return "Informação e Comunicação"
        elif prefixo in range(65, 67):
            return "Financeiro e Seguros"
        elif prefixo in range(68, 75):
            return "Serviços Profissionais"
        elif prefixo in range(77, 84):
            return "Administração Pública e Serviços Diversos"
        elif prefixo in range(85, 89):
            return "Educação e Saúde"
        elif prefixo in range(90, 94):
            return "Cultura, Esporte e Lazer"
        elif prefixo in range(95, 100):
            return "Serviços Domésticos"
        else:
            return "Outros"
    except:
        return "Desconhecido"


def corrigir_categoria_empresa(empresas):
    for empresa in empresas:
        usa_cnae20 = empresa.get("usa_CNAE_20", "N")
        cnae_code = empresa.get("CNAE_20") if usa_cnae20 == "S" else empresa.get("CNAE")
        empresa["ramo_atividade"] = categoria_por_cnae(cnae_code)
    return empresas