from odbc_reader.services import fetch_data
from get_empresas.services.get_client_data import get_nome_empresa
from collections import defaultdict


def get_socio(codigo_empresa):
    try:
        # CONSULTA ATUALIZADA com bethadba.gequadrosocietario_socios + bethadba.gesocios
        query = f"""
            SELECT 
                bethadba.gequadrosocietario_socios.codi_emp,
                bethadba.gequadrosocietario_socios.i_socio,
                bethadba.gesocios.nome
            FROM bethadba.gequadrosocietario_socios
            JOIN bethadba.gesocios 
              ON bethadba.gequadrosocietario_socios.i_socio = bethadba.gesocios.i_socio
            WHERE bethadba.gesocios.emancipado = 'N'
        """
        result = fetch_data(query)

        # Nome das empresas
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

        empresas_dict = defaultdict(list)
        for item in result:
            codi_emp = item["codi_emp"]
            nome_socio = item["nome"]
            empresas_dict[codi_emp].append(nome_socio)

        socios_dict = defaultdict(list)
        for item in result:
            codi_emp = item["codi_emp"]
            nome_socio = item["nome"]
            socios_dict[nome_socio].append(codi_emp)

        resultado = {}
        resultado["codi_emp"] = codigo_empresa
        resultado["nome_emp"] = consultaNome(codigo_empresa)["nome"]
        resultado["cnpj"] = consultaNome(codigo_empresa)["cnpj"]
        resultado["socios"] = empresas_dict[codigo_empresa]
        resultado["dados"] = []

        for i in empresas_dict[codigo_empresa]:
            lista_empresas = socios_dict[i]
            lista_empresas.remove(codigo_empresa)
            lista_nome_empresas = []
            for id in lista_empresas:
                nome_empresa = consultaNome(id)
                lista_nome_empresas.append(
                    {
                        "codi_emp": id,
                        "nome_emp": nome_empresa["nome"],
                        "cnpj": nome_empresa["cnpj"],
                    }
                )

            resultado["dados"].append({"socio": i, "empresas": lista_nome_empresas})

        return resultado

    except Exception as e:
        return {"error": str(e)}
