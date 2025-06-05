from django.http import JsonResponse
from odbc_reader.services import fetch_data
from get_empresas.services.get_client_data import get_empresa
import json
from datetime import datetime


# Função para formatar o formato do Horário em segundos
def format_log_time(start_date, start_time, end_date, end_time):
    # Combina data e hora em um único datetime
    formato = "%Y-%m-%d %H:%M:%S"

    inicio = datetime.strptime(f"{start_date} {start_time}", formato)
    fim = datetime.strptime(f"{end_date} {end_time}", formato)

    # Calcula a diferença em segundos (sempre positiva)
    return abs(int((fim - inicio).total_seconds()))


def get_lista_usuario():
    try:
        query = """SELECT 
                    i_usuario AS usuario, 
                    i_confusuario AS id_usuario,
                    SITUACAO AS situacao
                    FROM bethadba.usConfUsuario WHERE tipo = 1"""
        result = fetch_data(query)

    except Exception as e:

        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(result, safe=False)


def get_atividades_usuario(start_date, end_date):
    try:
        query = f"""
        SELECT * FROM bethadba.geloguser 
        WHERE data_log BETWEEN '{start_date}' AND '{end_date}'
        """
        result = fetch_data(query)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(result, safe=False)


def get_atividades_usuario_cliente(start_date, end_date):
    try:
        atividades = json.loads(get_atividades_usuario(start_date, end_date).content)
        empresas = json.loads(get_empresa().content)

        meses_abrev = [
            "jan",
            "fev",
            "mar",
            "abr",
            "mai",
            "jun",
            "jul",
            "ago",
            "set",
            "out",
            "nov",
            "dez",
        ]

        resultado = {}
        meses_encontrados = set()

        for atividade in atividades:
            usuario = atividade["usua_log"]
            empresa = atividade["codi_emp"]
            tempo_gasto = format_log_time(
                atividade["data_log"],  # Data de início (mesmo dia)
                atividade["tini_log"],  # Hora de início
                atividade["dfim_log"],  # Data real do fim (pode ser diferente)
                atividade["tfim_log"],  # Hora do fim
            )
            mes = int(
                datetime.strptime(atividade["data_log"], "%Y-%m-%d").strftime("%m")
            )

            meses_encontrados.add(mes)

            if empresa not in resultado:
                resultado[empresa] = {}

            if usuario not in resultado[empresa]:
                resultado[empresa][usuario] = {}

            if mes not in resultado[empresa][usuario]:
                resultado[empresa][usuario][mes] = 0

            resultado[empresa][usuario][mes] += tempo_gasto

        # Ordena os meses encontrados
        meses_ordenados = sorted(list(meses_encontrados))

        agrupado = []

        for empresa, usuarios in resultado.items():
            empresa_dados = {"codi_emp": empresa, "dados": [], "tempo_gasto_total": 0}

            for usuario, meses_dict in usuarios.items():
                usuario_data = {"usuario": usuario}
                total_usuario = 0

                for i in meses_ordenados:
                    tempo = meses_dict.get(i, 0)
                    usuario_data[meses_abrev[i - 1]] = tempo
                    total_usuario += tempo

                usuario_data["total"] = total_usuario
                empresa_dados["dados"].append(usuario_data)
                empresa_dados["tempo_gasto_total"] += total_usuario

            for empresa_info in empresas["Empresas"]:
                if empresa_info["codigo_empresa"] == empresa:
                    empresa_dados["nome_empresa"] = empresa_info["nome_empresa"]
                    break

            empresa_dados = {
                "nome_empresa": empresa_dados.get("nome_empresa", ""),
                **empresa_dados,
            }

            agrupado.append(empresa_dados)

        return JsonResponse(agrupado, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_atividades_usuario_modulo(start_date, end_date):
    module_mapping = {
        1: "Contabil",
        3: "Honorarios",
        4: "Patrimonio",
        5: "Escrita Fiscal",
        6: "Lalur",
        7: "Atualizar",
        8: "Protocolos",
        9: "Administrar",
        12: "Folha",
        13: "Ponto Eletronico",
        14: "Auditoria",
        15: "Registro",
    }

    meses_abrev = [
        "jan",
        "fev",
        "mar",
        "abr",
        "mai",
        "jun",
        "jul",
        "ago",
        "set",
        "out",
        "nov",
        "dez",
    ]

    try:
        total = json.loads(get_atividades_usuario(start_date, end_date).content)
        resultado = {"Atividades": {}}

        for atividade in total:
            usuario = atividade["usua_log"]
            modulo = atividade["sist_log"]
            tempo_gasto = format_log_time(
                atividade["data_log"],  # Data de início (mesmo dia)
                atividade["tini_log"],  # Hora de início
                atividade["dfim_log"],  # Data real do fim (pode ser diferente)
                atividade["tfim_log"],  # Hora do fim
            )

            data_log = datetime.strptime(atividade["data_log"], "%Y-%m-%d")
            mes_abreviado = meses_abrev[data_log.month - 1]

            modulo_nome = module_mapping.get(modulo, f"Modulo {modulo}")

            if modulo_nome not in resultado["Atividades"]:
                resultado["Atividades"][modulo_nome] = {}

            if usuario not in resultado["Atividades"][modulo_nome]:
                resultado["Atividades"][modulo_nome][usuario] = {}

            if mes_abreviado not in resultado["Atividades"][modulo_nome][usuario]:
                resultado["Atividades"][modulo_nome][usuario][mes_abreviado] = 0

            resultado["Atividades"][modulo_nome][usuario][mes_abreviado] += tempo_gasto

        return JsonResponse(resultado, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
