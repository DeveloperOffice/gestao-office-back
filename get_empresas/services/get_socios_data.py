from odbc_reader.services import fetch_data
from get_empresas.services.get_client_data import get_nome_empresa
from collections import defaultdict


def get_socio(codigo_empresa):
    try:

        query = f"""
                SELECT
                FOCONTRIBUINTES.CODI_EMP,
                FOCONTRIBUINTES.I_CONTRIBUINTES,
                FOCONTRIBUINTES.NOME,
                FOCONTRIBUINTES.TIPO
                FROM bethadba.FOCONTRIBUINTES
                WHERE FOCONTRIBUINTES.TIPO = 'E' AND FOCONTRIBUINTES.DESLIGADO = 'N'
                """
        result = fetch_data(query)

        # Pegando o nome de todas as empresas junto com o código para vincular aos socios
        nomeEmpresas = get_nome_empresa()

        # Inicializando um dicionário para armazenar empresas e seus sócios
        empresas_dict = defaultdict(list)

        for item in result:
            codi_emp = item["CODI_EMP"]
            nome_socio = item["NOME"]

            # Adiciona o nome do sócio na lista da empresa (identificada pelo codi_emp)
            empresas_dict[codi_emp].append(nome_socio)

        # Inicializando um dicionário para armazenar os sócios e as empresas em que eles estão
        socios_dict = defaultdict(list)

        # Iterando sobre os dados novamente para preencher as empresas de cada sócio
        for item in result:
            codi_emp = item["CODI_EMP"]
            nome_socio = item["NOME"]

            # Adiciona a empresa à lista de empresas do sócio
            socios_dict[nome_socio].append(codi_emp)

        # O dicionário socios_dict agora terá o nome do sócio como chave e uma lista de empresas como valor

        # Criando o resultado a partir do codigo da empresa fornecido ligando aos dicionários
        resultado = {}
        resultado["codi_emp"] = codigo_empresa
        resultado["socios"] = empresas_dict[codigo_empresa]
        resultado["dados"] = []

        # Interando sobre os sócios no dicionário da empresa
        for i in empresas_dict[codigo_empresa]:
            lista_empresas = socios_dict[i]
            lista_empresas.remove(
                codigo_empresa
            )  # Remove a 1º empresa para não aparecer novamente.
            resultado["dados"].append({"socio": i, "empresas": lista_empresas})

        return resultado

    except Exception as e:
        return {"error": str(e)}
