from odbc_reader.services import fetch_data
from datetime import datetime

hoje = datetime.now().strftime("%Y-%m-%d")


def get_ficha(start_date, end_date):
    try:
        query = f"""SELECT
            foempregados.codi_emp AS empresa,
            geempre.nome_emp AS nome_empresa,
            geempre.cgce_emp AS cnpj,
            foempregados.i_empregados AS id_empregado,
            foempregados.nome,
            foempregados.data_nascimento,
            foempregados.cpf,
            focargos.nome AS cargo,
            foempregados.sexo,
            foempregados.estado_civil,
            foempregados.grau_instrucao AS escolaridade,
            fodepto.nome AS departamento,
            foempregados.horas_mes,
            foempregados.horas_semana,
            foempregados.horas_dia,
            foempregados.admissao,
            forescisoes.demissao,
            foempregados.salario,
            foempregados.venc_ferias
    
            FROM bethadba.foempregados 
            INNER JOIN bethadba.geempre ON foempregados.codi_emp = geempre.codi_emp AND geempre.stat_emp = 'A'
            INNER JOIN bethadba.focargos ON foempregados.i_cargos = focargos.i_cargos AND focargos.SITUACAO = 1 AND focargos.codi_emp = foempregados.codi_emp
            INNER JOIN bethadba.fodepto ON foempregados.i_depto = fodepto.i_depto AND fodepto.codi_emp = foempregados.codi_emp
            INNER JOIN bethadba.forescisoes ON foempregados.i_empregados = forescisoes.i_empregados AND forescisoes.codi_emp = foempregados.codi_emp AND forescisoes.demissao > {hoje}
            """
        query2 = f"""SELECT * FROM bethadba.foeventos"""
        result = fetch_data(query)
        result2 = fetch_data(query2)
        # Dicionário para escolaridade
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

        # Dicionário para estado civil
        estadosCivis = {
            "C": "Casado",
            "D": "Divorciado",
            "J": "Separado judicialmente",
            "O": "Concubinado",
            "S": "Solteiro",
            "U": "União estável",
            "V": "Viúvo",
        }

        # Criar um dicionário para agrupar funcionários por empresa
        empresas_dict = {}

        for row in result:
            empresa = row["empresa"]
            nome_empresa = row["nome_empresa"]
            cnpj = row["cnpj"]
            funcionario = {
                "id_empregado": row["id_empregado"],
                "nome": row["nome"],
                "data_nascimento": row["data_nascimento"],
                "cpf": row["cpf"],
                "cargo": row["cargo"],
                "sexo": row["sexo"],
                "estado_civil": estadosCivis.get(row["estado_civil"], "Não informado"),
                "escolaridade": niveisEscolaridade[row["escolaridade"]],
                "departamento": row["departamento"],
                "horas_mes": row["horas_mes"],
                "horas_semana": row["horas_semana"],
                "horas_dia": row["horas_dia"],
                "admissao": row["admissao"],
                "salario": row["salario"],
                "venc_ferias": row["venc_ferias"],
            }

            if empresa not in empresas_dict:
                empresas_dict[empresa] = {
                    "id_empresa": empresa,
                    "nome_empresa": nome_empresa,
                    "cnpj": cnpj,
                    "funcionarios": [],
                }

            empresas_dict[empresa]["funcionarios"].append(funcionario)

        # Converter o dicionário para uma lista de empresas
        lista_empresas = list(empresas_dict.values())

        return lista_empresas

    except Exception as e:
        return {"error": str(e)}
