from odbc_reader.services import fetch_data
from get_empresas.services.get_client_data import get_nome_empresa
from collections import defaultdict


def get_socio(codigo_empresa):
    try:
        query = f"""
            SELECT 
                bethadba.gequadrosocietario_socios.codi_emp,
                bethadba.gequadrosocietario_socios.i_socio,
                bethadba.gesocios.nome,
                bethadba.gesocios.inscricao  
            FROM bethadba.gequadrosocietario_socios
            JOIN bethadba.gesocios 
              ON bethadba.gequadrosocietario_socios.i_socio = bethadba.gesocios.i_socio
            WHERE bethadba.gesocios.emancipado = 'N'
        """
        result = fetch_data(query)
        nomeEmpresas = get_nome_empresa()

        def consultaNome(code):
            empresa = next(
                (empresa for empresa in nomeEmpresas if empresa["codi_emp"] == code),
                None,
            )
            if not empresa:
                print({"error": f"Nenhuma empresa encontrada com codi_emp {code}."})
                return None
            return {
                "nome": empresa["nome_emp"],
                "cnpj": empresa.get("cnpj", "CNPJ não informado"),
            }

        empresas_dict = defaultdict(set)  # usa set para evitar duplicatas
        for item in result:
            codi_emp = item["codi_emp"]
            nome_socio = item["nome"]
            empresas_dict[codi_emp].add(nome_socio)

        socios_dict = defaultdict(set)  # mesma ideia
        for item in result:
            codi_emp = item["codi_emp"]
            nome_socio = item["nome"]
            socios_dict[nome_socio].add(codi_emp)

        resultado = {
            "codi_emp": codigo_empresa,
            "nome_emp": consultaNome(codigo_empresa)["nome"] if consultaNome(codigo_empresa) else "Nome não encontrado",
            "cnpj": consultaNome(codigo_empresa)["cnpj"] if consultaNome(codigo_empresa) else "CNPJ não encontrado",
            "socios": sorted(empresas_dict[codigo_empresa]),  # ordenado pra ficar bonito
            "dados": []
        }

        # Itera sobre sócios únicos
        for socio in empresas_dict[codigo_empresa]:
            empresas_socio = socios_dict[socio] - {codigo_empresa}  # remove a empresa principal
            lista_nome_empresas = []

            for id in empresas_socio:
                nome_empresa = consultaNome(id)
                if nome_empresa:
                    lista_nome_empresas.append({
                        "codi_emp": id,
                        "nome_emp": nome_empresa["nome"],
                        "cnpj": nome_empresa["cnpj"]
                    })

            # Recuperando o CPF (inscricao) diretamente do result
            socio_info = next((item for item in result if item["nome"] == socio), None)
            if socio_info:  # Verifica se socio_info não é None
                resultado["dados"].append({
                    "socio": socio,
                    "CPF": socio_info["inscricao"],  # Agora o CPF vem direto de result
                    "empresas": lista_nome_empresas
                })
            else:
                print(f"Erro ao encontrar CPF para o sócio {socio}")  # Log de erro
                resultado["dados"].append({
                    "socio": socio,
                    "CPF": "CPF não encontrado",  # Ou outra mensagem de erro
                    "empresas": lista_nome_empresas
                })

        return resultado

    except Exception as e:
        return {"error": str(e)}
