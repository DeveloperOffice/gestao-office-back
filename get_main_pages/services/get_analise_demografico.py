from odbc_reader.services import fetch_data

def get_demografico(start_date, end_date):
    query = f"""
    SELECT
        foempregados.codi_emp AS empresa,
        geempre.nome_emp AS nome_empresa,
        geempre.cgce_emp AS cnpj,
        foempregados.i_empregados AS id_empregado,
        foempregados.nome,
        foempregados.data_nascimento,
        foempregados.cpf,
        focargos.nome AS cargo,
        foempregados.sexo,
        foempregados.grau_instrucao AS escolaridade,
        fodepto.nome AS departamento,
        foempregados.admissao,
        forescisoes.demissao,
        foempregados.salario,
        foempregados.venc_ferias,
        foempregados.categoria
    FROM bethadba.foempregados 
    INNER JOIN bethadba.geempre 
        ON foempregados.codi_emp = geempre.codi_emp 
        AND geempre.stat_emp = 'A'
    INNER JOIN bethadba.focargos 
        ON foempregados.i_cargos = focargos.i_cargos 
        AND focargos.SITUACAO = 1 
        AND focargos.codi_emp = foempregados.codi_emp
    INNER JOIN bethadba.fodepto 
        ON foempregados.i_depto = fodepto.i_depto 
        AND fodepto.codi_emp = foempregados.codi_emp
    LEFT JOIN bethadba.forescisoes 
        ON foempregados.i_empregados = forescisoes.i_empregados 
        AND forescisoes.codi_emp = foempregados.codi_emp
    WHERE foempregados.admissao BETWEEN '{start_date}' AND '{end_date}'
    """
    
    result = fetch_data(query)

    query_afastamentos = f"""
    SELECT
        CODI_EMP,
        I_EMPREGADOS,
        DATA_REAL AS data_inicio,
        DATA_FIM AS data_fim
    FROM bethadba.FOAFASTAMENTOS
    WHERE DATA_REAL >= '{start_date}' AND DATA_REAL <= '{end_date}'
    """
    afastamentos = fetch_data(query_afastamentos)

    afastamentos_dict = {}
    for a in afastamentos:
        key = (a["CODI_EMP"], a["I_EMPREGADOS"])
        if key not in afastamentos_dict:
            afastamentos_dict[key] = []
        afastamentos_dict[key].append({
            "data_inicio": a["data_inicio"],
            "data_fim": a["data_fim"]
        })

    niveisEscolaridade = {
        1: "Analfabeto",
        2: "Ensino Fundamental I incompleto",
        3: "Ensino Fundamental I completo",
        4: "Ensino Fundamental II incompleto",
        5: "Ensino Fundamental II completo",
        6: "Ensino médio incompleto",
        7: "Ensino médio completo",
        8: "Superior incompleto",
        9: "Superior completo",
        10: "Mestrado",
        11: "Doutorado",
        12: "Ph. D.",
        13: "Pós Graduação",
    }

    empresas_dict = {}  

    for row in result:
        id_empresa = row["empresa"]
        if id_empresa not in empresas_dict:
            empresas_dict[id_empresa] = {
                "id_empresa": id_empresa,
                "nome_empresa": row["nome_empresa"],
                "cnpj": row["cnpj"],
                "funcionarios": []
            }

        key = (row["empresa"], row["id_empregado"])
        funcionario_afastamentos = afastamentos_dict.get(key, [])

        funcionario = {
            "id_empregado": row["id_empregado"],
            "nome": row["nome"],
            "data_nascimento": row["data_nascimento"],
            "cpf": row["cpf"],
            "sexo": row["sexo"],
            "escolaridade": niveisEscolaridade.get(row["escolaridade"], "Não informado"),
            "departamento": row["departamento"],
            "admissao": row["admissao"],
            "demissao": row["demissao"],
            "salario": row["salario"],
            "venc_ferias": row["venc_ferias"],
            "cargo": row["cargo"],
            "categoria": row["categoria"],
            "afastamentos": funcionario_afastamentos
        }

        empresas_dict[id_empresa]["funcionarios"].append(funcionario)

    dados = list(empresas_dict.values())

    return {"dados": dados}  