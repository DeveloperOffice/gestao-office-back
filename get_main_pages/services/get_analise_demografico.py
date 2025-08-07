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
        ultima_rescisao.demissao,
        ultima_rescisao.motivo_demissao,
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
    LEFT JOIN (
        SELECT
            codi_emp,
            i_empregados,
            MAX(demissao) AS demissao,
            MAX(motivo) AS motivo_demissao
        FROM bethadba.forescisoes
        GROUP BY codi_emp, i_empregados
    ) AS ultima_rescisao
        ON foempregados.codi_emp = ultima_rescisao.codi_emp
        AND foempregados.i_empregados = ultima_rescisao.i_empregados
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
        0: "Não informado",
        1: "Analfabeto",
        2: "Ensino Fundamental até 5º Incompleto",
        3: "Ensino Fundamental 5º Completo",
        4: "Ensino Fundamental 6º ao 9º",
        5: "Ensino Fundamental Completo",
        6: "Ensino Médio Incompleto",
        7: "Ensino Médio Completo",
        8: "Superior Incompleto",
        9: "Superior Completo",
        10: "Mestrado",
        11: "Doutorado",
        12: "Ph. D",
        13: "Pós-Graduação"
    }

    categorias = {
        1: "Mensalista",
        2: "Quinzenista",
        3: "Semanalista",
        4: "Diarista",
        5: "Horista",
        6: "Tarefa",
        7: "Comissão",
        8: "Diretoria",
        9: "Mensalista",
        10: "Mensalista",
        11: "Aulista",
        12: "Aulista Variável",
        13: "Outros"
    }

    motivos_rescisao = {
        1: "Demitido COM justa causa",
        2: "Demitido SEM justa causa",
        3: "Rescisão indireta",
        4: "Pedido de demissão SEM justa causa",
        5: "Cessão do empregado",
        6: "Transferência sem ônus p/ mesma empresa",
        8: "Morte",
        10: "Rescisão de experiência (empregador)",
        11: "Rescisão de experiência (empregado)",
        12: "Término contrato de experiência",
        13: "Morte por acidente de trabalho",
        14: "Morte por doença profissional",
        22: "Término do contrato determinado",
        23: "Antecipado pelo empregador (determinado)",
        24: "Antecipado pelo empregado (determinado)",
        27: "Transferência sem ônus p/ outra empresa",
        28: "Culpa recíproca",
        29: "Extinção da empresa",
        30: "Extinção por força maior",
        40: "Morte por acidente de trajeto",
        41: "Falecimento empregador sem continuidade",
        42: "Falecimento empregador - opção empregado"
    }

    empresas_dict = {}

    for row in result:
        id_empresa = row["empresa"]
        if id_empresa not in empresas_dict:
            empresas_dict[id_empresa] = {
                "id_empresa": id_empresa,
                "nome_empresa": row["nome_empresa"],
                "cnpj": row["cnpj"],
                "empregados_ativos": 0,
                "funcionarios": []
            }

        key = (row["empresa"], row["id_empregado"])
        funcionario_afastamentos = afastamentos_dict.get(key, [])

        ativo = row["demissao"] is None or row["admissao"] > row["demissao"]

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
            "motivo_demissao": motivos_rescisao.get(row.get("motivo_demissao"), "Não informado"),
            "salario": row["salario"],
            "venc_ferias": row["venc_ferias"],
            "cargo": row["cargo"],
            "categoria": categorias.get(row["categoria"], "Não informado"),
            "afastamentos": funcionario_afastamentos,
            "situacao": "Ativo" if ativo else "Inativo"
        }

        if ativo:
            empresas_dict[id_empresa]["empregados_ativos"] += 1

        empresas_dict[id_empresa]["funcionarios"].append(funcionario)

    dados = list(empresas_dict.values())

    return {"dados": dados}
