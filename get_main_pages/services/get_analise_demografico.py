from odbc_reader.services import fetch_data

def get_demografico(start_date, end_date):
    query = f"""
    SELECT 
        foempregados.codi_emp,
        foempregados.i_empregados,
        foempregados.admissao,
        foempregados.salario,
        foempregados.sexo,
        foempregados.cpf,
        foempregados.grau_instrucao,
        foempregados.nome,
        geempre.nome_emp AS nome_empresa,
        foempregados.estado_civil,
        foempregados.data_nascimento,
        foempregados.venc_ferias
    FROM bethadba.foempregados
    INNER JOIN bethadba.geempre ON foempregados.codi_emp = geempre.codi_emp
    """
    result = fetch_data(query)

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
        id_empresa = row["codi_emp"]
        if id_empresa not in empresas_dict:
            empresas_dict[id_empresa] = {
                "id_empresa": id_empresa,
                "nome_empresa": row["nome_empresa"],
                "funcionarios": []
            }

        funcionario = {
            "id_empregado": row["i_empregados"],
            "nome": row["nome"],
            "data_nascimento": row["data_nascimento"],
            "cpf": row["cpf"],
            "sexo": row["sexo"],
            "estado_civil": row["estado_civil"],
            "escolaridade": niveisEscolaridade.get(row["grau_instrucao"], "Não informado"),
            "admissao": row["admissao"],
            "salario": row["salario"],
            "venc_ferias": row["venc_ferias"],
        }

        empresas_dict[id_empresa]["funcionarios"].append(funcionario)

    dados = list(empresas_dict.values())

    return {"dados": dados}  