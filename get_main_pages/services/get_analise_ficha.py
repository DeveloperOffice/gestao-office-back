from odbc_reader.services import fetch_data
from datetime import datetime

hoje = datetime.now().strftime("%Y-%m-%d")


def get_ficha(start_date, end_date):
    try:
        # Query principal de funcionários
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
            INNER JOIN bethadba.forescisoes 
                ON foempregados.i_empregados = forescisoes.i_empregados 
                AND forescisoes.codi_emp = foempregados.codi_emp 
                AND forescisoes.demissao > {hoje}
        """

        # Query de afastamentos
        queryAfastamentos = f"""
            SELECT
                FOAFASTAMENTOS.CODI_EMP,
                FOAFASTAMENTOS.I_EMPREGADOS,
                FOAFASTAMENTOS_TIPOS.DESCRICAO,
                FOAFASTAMENTOS.DATA_REAL,
                FOAFASTAMENTOS.DATA_FOLHA,
                FOAFASTAMENTOS.I_AFASTAMENTOS,
                FOAFASTAMENTOS.DATA_FIM,
                FOAFASTAMENTOS.DATA_FIM_TMP,
                FOAFASTAMENTOS.NUMERO_DIAS
            FROM bethadba.FOAFASTAMENTOS 
            INNER JOIN bethadba.FOAFASTAMENTOS_TIPOS 
                ON FOAFASTAMENTOS.I_AFASTAMENTOS = FOAFASTAMENTOS_TIPOS.I_AFASTAMENTOS
            WHERE DATA_REAL > '{start_date}' 
            AND DATA_REAL < '{end_date}'
        """

        # Query de exames
        queryExames = f"""
            SELECT
                FOMONITORAMENTO_SAUDE_TRABALHADOR.CODI_EMP,
                FOMONITORAMENTO_SAUDE_TRABALHADOR.I_EMPREGADOS,
                FOMONITORAMENTO_SAUDE_TRABALHADOR.SEQUENCIAL,
                FOMONITORAMENTO_SAUDE_TRABALHADOR.DATA_ASO,
                FOMONITORAMENTO_SAUDE_TRABALHADOR.VENCIMENTO_ASO,
                CASE FOMONITORAMENTO_SAUDE_TRABALHADOR.TIPO_ASO
                    WHEN 1 THEN 'Admissional'
                    WHEN 2 THEN 'Periódico'
                    WHEN 3 THEN 'Retorno ao trabalho'
                    WHEN 4 THEN 'Mudança de função'
                    WHEN 5 THEN 'Monitoração pontual'
                    WHEN 6 THEN 'Demissional'
                    ELSE 'Outro'
                END AS TIPO_ASO_DESC,
                CASE FOMONITORAMENTO_SAUDE_TRABALHADOR.RESULTADO
                    WHEN 1 THEN 'Apto'
                    WHEN 2 THEN 'Inapto'
                    ELSE 'Indefinido'
                END AS RESULTADO
            FROM bethadba.FOMONITORAMENTO_SAUDE_TRABALHADOR 
            WHERE DATA_ASO > '{start_date}' 
            AND VENCIMENTO_ASO < '{end_date}'
        """

        # Query de alterações salariais
        queryAlteracoesSalarios = f"""
            SELECT
                foaltesal.codi_emp,
                foaltesal.i_empregados,
                foempregados.nome,
                foaltesal.competencia,
                foaltesal.novo_salario,
                foaltesal.motivo,
                foaltesal.salario_anterior
            FROM bethadba.foaltesal
            INNER JOIN bethadba.foempregados 
                ON foempregados.i_empregados = foaltesal.i_empregados 
                AND foempregados.codi_emp = foaltesal.codi_emp
        """

        result = fetch_data(query)
        resultAfastamentos = fetch_data(queryAfastamentos)
        resultExames = fetch_data(queryExames)
        resultSalarios = fetch_data(queryAlteracoesSalarios)

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
                "admissao": row["admissao"],
                "salario": row["salario"],
                "venc_ferias": row["venc_ferias"],
                "afastamentos": [],
                "exames": [],
            }

            # Montando afastamentos dentro da empresa
            for afastamento in resultAfastamentos:
                if (
                    row["empresa"] == afastamento["CODI_EMP"]
                    and row["id_empregado"] == afastamento["I_EMPREGADOS"]
                ):
                    funcionario["afastamentos"].append(
                        {
                            "data_inicial": afastamento["DATA_FOLHA"],
                            "data_final": afastamento["DATA_FIM"],
                            "num_dias": afastamento["NUMERO_DIAS"],
                            "tipo": afastamento["DESCRICAO"],
                        }
                    )

            # Montando exames dentro da empresa
            for exame in resultExames:
                if (
                    row["empresa"] == exame["CODI_EMP"]
                    and row["id_empregado"] == exame["I_EMPREGADOS"]
                ):
                    funcionario["exames"].append(
                        {
                            "data_inicial": exame["DATA_ASO"],
                            "data_vencimento": exame["VENCIMENTO_ASO"],
                            "resultado": exame["RESULTADO"],
                            "tipo": exame["TIPO_ASO_DESC"],
                        }
                    )

            # Montando Lista completa
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

        # Criar um dicionário para agrupar alterações sálariais por empresa
        salariosdict = {}

        for row in resultSalarios:
            id_empresa = row["codi_emp"]
            id_empregado = row["i_empregados"]

            # Se a empresa não existe no dicionário, cria a estrutura básica
            if id_empresa not in salariosdict:
                salariosdict[id_empresa] = {"id_empresa": id_empresa, "alteracoes": []}

            # Adiciona a alteração salarial
            salariosdict[id_empresa]["alteracoes"].append(
                {
                    "id_empregado": id_empregado,
                    "nome": row["nome"],
                    "competencia": row["competencia"],
                    "novo_salario": row["novo_salario"],
                    "salario_anterior": row["salario_anterior"],
                    "motivo": row["motivo"],
                }
            )

        # Resultado final
        lista_alteracoes_salariais = list(salariosdict.values())

        return {
            "dados": lista_empresas,
            "alteracao_salario": lista_alteracoes_salariais,
        }

    except Exception as e:
        return {"error": str(e)}
