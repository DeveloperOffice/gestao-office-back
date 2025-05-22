from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime
import json
import logging
import traceback

logger = logging.getLogger(__name__)

# Mapeamento único para meses: abreviação -> número e inverso
MESES_ABREV_TO_NUM = {
    "jan": 1,
    "fev": 2,
    "mar": 3,
    "abr": 4,
    "mai": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "out": 10,
    "nov": 11,
    "dez": 12,
}
MES_NUM_TO_ABREV = {v: k for k, v in MESES_ABREV_TO_NUM.items()}


def time_to_seconds(t):
    """Converte um objeto datetime.time ou string 'HH:MM:SS' para segundos."""
    if t is None:
        return 0
    if isinstance(t, str):
        try:
            t = datetime.strptime(t, "%H:%M:%S").time()
        except Exception:
            return 0
    return t.hour * 3600 + t.minute * 60 + t.second


def get_usuarios():
    try:
        query = """
        SELECT NOME AS nome_usuario, user_id AS id_usuario
        FROM bethadba.usConfUsuario
        """
        resultados = fetch_data(query)
        return {str(u["id_usuario"]): u["nome_usuario"] for u in resultados}
    except Exception as e:
        logger.error(f"Erro ao carregar usuários: {e}")
        return {}


def get_tempo_gasto_usuario_empresa_mes(start_date, end_date):
    """Retorna dicionário com tempo gasto (em segundos) por usuário, empresa e mês/ano."""
    try:
        query = f"""
        SELECT
            codi_emp,
            usua_log AS codi_usu,
            data_log,
            SUM(DATEDIFF(SECOND, tini_log, tfim_log)) AS tempo_segundos
        FROM bethadba.geloguser
        WHERE data_log BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, usua_log, data_log
        """
        resultados = fetch_data(query)

        dados = {}
        for row in resultados:
            if isinstance(row, bytes):
                row = json.loads(row.decode("utf-8"))

            usuario_id = str(row["codi_usu"])
            codi_emp = row["codi_emp"]
            data = row["data_log"]
            if isinstance(data, str):
                data = datetime.strptime(data, "%Y-%m-%d")

            mes = data.month
            ano = data.year
            nome_mes = f"{MES_NUM_TO_ABREV[mes]}/{ano}"

            dados.setdefault(usuario_id, {}).setdefault(codi_emp, {})
            dados[usuario_id][codi_emp][nome_mes] = dados[usuario_id][codi_emp].get(
                nome_mes, 0
            ) + row.get("tempo_segundos", 0)

        return dados
    except Exception as e:
        logger.error(f"Erro ao carregar tempo gasto: {e}")
        return {}


def agrupar_por_usuario_empresa_mes(query_result, data_key):
    """Agrupa contagens por usuário, empresa e mês/ano."""
    dados = {}
    for row in query_result:
        if isinstance(row, bytes):
            row = json.loads(row.decode("utf-8"))

        usuario_id = str(row["codi_usu"])
        codi_emp = row["codi_emp"]
        data = row[data_key]
        if isinstance(data, str):
            data = datetime.strptime(data, "%Y-%m-%d")

        mes = data.month
        ano = data.year
        nome_mes = f"{MES_NUM_TO_ABREV[mes]}/{ano}"

        dados.setdefault(usuario_id, {}).setdefault(codi_emp, {})
        dados[usuario_id][codi_emp][nome_mes] = (
            dados[usuario_id][codi_emp].get(nome_mes, 0) + row["total_ocorrencias"]
        )

    return dados


def get_analise_usuario(start_date, end_date):
    try:
        usuarios_map = get_usuarios()

        # Queries para contagem
        query_saida = f"""
        SELECT codi_emp, codi_usu, dsai_sai AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.efsaidas
        WHERE dsai_sai BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, codi_usu, dsai_sai
        """

        query_entrada = f"""
        SELECT codi_emp, codi_usu, dent_ent AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.efentradas
        WHERE dent_ent BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, codi_usu, dent_ent
        """

        query_servicos = f"""
        SELECT codi_emp, codi_usu, dser_ser AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.efservicos
        WHERE dser_ser BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, codi_usu, dser_ser
        """

        query_lancamentos = f"""
        SELECT codi_emp, codi_usu, data_lan AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.ctlancto
        WHERE data_lan BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY codi_emp, codi_usu, data_lan
        """

        query_lancamentos_manuais = f"""
        SELECT codi_emp, codi_usu, data_lan AS data_ref, COUNT(*) AS total_ocorrencias
        FROM bethadba.ctlancto
        WHERE data_lan BETWEEN '{start_date}' AND '{end_date}'
          AND origem_lan = 1
        GROUP BY codi_emp, codi_usu, data_lan
        """

        saidas = agrupar_por_usuario_empresa_mes(fetch_data(query_saida), "data_ref")
        entradas = agrupar_por_usuario_empresa_mes(
            fetch_data(query_entrada), "data_ref"
        )
        servicos = agrupar_por_usuario_empresa_mes(
            fetch_data(query_servicos), "data_ref"
        )
        lancamentos = agrupar_por_usuario_empresa_mes(
            fetch_data(query_lancamentos), "data_ref"
        )
        lancamentos_manuais = agrupar_por_usuario_empresa_mes(
            fetch_data(query_lancamentos_manuais), "data_ref"
        )
        tempo_gasto = get_tempo_gasto_usuario_empresa_mes(start_date, end_date)

        todos_usuarios = set()
        for d in [
            saidas,
            entradas,
            servicos,
            lancamentos,
            lancamentos_manuais,
            tempo_gasto,
        ]:
            todos_usuarios.update(d.keys())

        resultado_final = []

        for usuario_id in todos_usuarios:
            empresas = set()
            for fonte in [
                saidas,
                entradas,
                servicos,
                lancamentos,
                lancamentos_manuais,
                tempo_gasto,
            ]:
                if usuario_id in fonte:
                    empresas.update(fonte[usuario_id].keys())

            total_usuario_entradas = total_usuario_saidas = total_usuario_servicos = 0
            total_usuario_lancamentos = total_usuario_lancamentos_manuais = (
                total_usuario_tempo_gasto
            ) = 0
            empresas_list = []

            for codi_emp in empresas:
                meses_todos = set()
                for fonte in [
                    saidas,
                    entradas,
                    servicos,
                    lancamentos,
                    lancamentos_manuais,
                    tempo_gasto,
                ]:
                    meses_todos.update(
                        fonte.get(usuario_id, {}).get(codi_emp, {}).keys()
                    )

                meses_ordenados = sorted(
                    meses_todos,
                    key=lambda x: (
                        int(x.split("/")[1]),
                        MESES_ABREV_TO_NUM[x.split("/")[0]],
                    ),
                )

                total_entradas = total_saidas = total_servicos = 0
                total_lancamentos = total_lancamentos_manuais = (
                    total_tempo_gasto_empresa
                ) = 0
                dados_empresa = {}

                for mes in meses_ordenados:
                    e = entradas.get(usuario_id, {}).get(codi_emp, {}).get(mes, 0)
                    s = saidas.get(usuario_id, {}).get(codi_emp, {}).get(mes, 0)
                    svc = servicos.get(usuario_id, {}).get(codi_emp, {}).get(mes, 0)
                    l = lancamentos.get(usuario_id, {}).get(codi_emp, {}).get(mes, 0)
                    lm = (
                        lancamentos_manuais.get(usuario_id, {})
                        .get(codi_emp, {})
                        .get(mes, 0)
                    )
                    tg = tempo_gasto.get(usuario_id, {}).get(codi_emp, {}).get(mes, 0)

                    importacoes = e + s + svc
                    dados_empresa[mes] = {
                        "tempo_gasto": tg,
                        "importacoes": importacoes,
                        "lancamentos": l,
                        "lancamentos_manuais": lm,
                    }

                    total_entradas += e
                    total_saidas += s
                    total_servicos += svc
                    total_lancamentos += l
                    total_lancamentos_manuais += lm
                    total_tempo_gasto_empresa += tg

                total_empresa = (
                    total_entradas
                    + total_saidas
                    + total_servicos
                    + total_lancamentos
                    + total_lancamentos_manuais
                )
                empresas_list.append(
                    {
                        "codi_emp": codi_emp,
                        "atividades": dados_empresa,
                        "total_entradas": total_entradas,
                        "total_saidas": total_saidas,
                        "total_servicos": total_servicos,
                        "total_lancamentos": total_lancamentos,
                        "total_lancamentos_manuais": total_lancamentos_manuais,
                        "total_tempo_gasto": total_tempo_gasto_empresa,
                        "total_importacoes": total_entradas
                        + total_saidas
                        + total_servicos,
                        "total_geral": total_empresa,
                    }
                )

                total_usuario_entradas += total_entradas
                total_usuario_saidas += total_saidas
                total_usuario_servicos += total_servicos
                total_usuario_lancamentos += total_lancamentos
                total_usuario_lancamentos_manuais += total_lancamentos_manuais
                total_usuario_tempo_gasto += total_tempo_gasto_empresa

            total_geral_usuario = (
                total_usuario_entradas
                + total_usuario_saidas
                + total_usuario_servicos
                + total_usuario_lancamentos
                + total_usuario_lancamentos_manuais
            )
            resultado_final.append(
                {
                    "usuario_id": usuario_id,
                    "nome_usuario": usuarios_map.get(usuario_id, usuario_id),
                    "empresas": empresas_list,
                    "total_entradas": total_usuario_entradas,
                    "total_saidas": total_usuario_saidas,
                    "total_servicos": total_usuario_servicos,
                    "total_lancamentos": total_usuario_lancamentos,
                    "total_lancamentos_manuais": total_usuario_lancamentos_manuais,
                    "total_tempo_gasto": total_usuario_tempo_gasto,
                    "total_importacoes": total_usuario_entradas
                    + total_usuario_saidas
                    + total_usuario_servicos,
                    "total_geral": total_geral_usuario,
                }
            )

        # Cálculo dos totais gerais
        totais_gerais = {
            "total_entradas": sum(u["total_entradas"] for u in resultado_final),
            "total_saidas": sum(u["total_saidas"] for u in resultado_final),
            "total_servicos": sum(u["total_servicos"] for u in resultado_final),
            "total_lancamentos": sum(u["total_lancamentos"] for u in resultado_final),
            "total_lancamentos_manuais": sum(
                u["total_lancamentos_manuais"] for u in resultado_final
            ),
            "total_tempo_gasto": sum(u["total_tempo_gasto"] for u in resultado_final),
            "total_importacoes": sum(u["total_importacoes"] for u in resultado_final),
            "total_geral": sum(u["total_geral"] for u in resultado_final),
        }

        return JsonResponse(
            {"analises": resultado_final, "totais_gerais": totais_gerais}, safe=False
        )

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Erro: {e}\n{tb}")
        return JsonResponse({"error": str(e), "traceback": tb}, status=500)


def get_analise_por_sistema(start_date, end_date):
    try:

        sistemas = {
            1: "Contabil",
            3: "Honorários",
            4: "Patrimônio",
            5: "Escrita Fiscal",
            6: "Lalur",
            7: "Atualizar",
            8: "Protocolos",
            9: "Administrar",
            12: "Folha de Pagamento",
            13: "Ponto Eletrônico",
            14: "Auditoria",
            15: "Registro",
        }

        query = f"""
        SELECT
            geloguser.sist_log AS sistema,
            geloguser.usua_log AS usuario,
            geloguser.data_log AS data_log,
            geloguser.tini_log AS inicio_log,
            geloguser.tfim_log AS fim_log
        FROM bethadba.geloguser
        WHERE geloguser.data_log BETWEEN '{start_date}' AND '{end_date}'
        """
        registros = fetch_data(query)

        resultado = {}
        for registro in registros:
            sistema = sistemas[registro["sistema"]]
            if sistema not in sistemas.values():
                continue
            usuario = registro["usuario"]
            data_log = registro["data_log"]
            inicio_log = registro["inicio_log"]
            fim_log = registro["fim_log"]

            if isinstance(data_log, str):
                data_log = datetime.strptime(data_log, "%Y-%m-%d")
            inicio_segundos = time_to_seconds(inicio_log)
            fim_segundos = time_to_seconds(fim_log)
            duracao = fim_segundos - inicio_segundos
            if duracao < 0:
                duracao += 24 * 3600
            mes_ano = f"{MES_NUM_TO_ABREV[data_log.month]}/{data_log.year}"

            resultado.setdefault(sistema, {}).setdefault(usuario, {})
            resultado[sistema][usuario][mes_ano] = (
                resultado[sistema][usuario].get(mes_ano, 0) + duracao
            )

        resposta = {}
        for sistema, usuarios in resultado.items():
            total_sistema = 0
            usuarios_list = []
            for usuario, meses in usuarios.items():
                meses_ordenados = sorted(
                    meses.items(),
                    key=lambda x: (
                        int(x[0].split("/")[1]),
                        MESES_ABREV_TO_NUM[x[0].split("/")[0]],
                    ),
                )
                atividades = {mes: tempo for mes, tempo in meses_ordenados}
                total_usuario = sum(atividades.values())
                total_sistema += total_usuario
                usuarios_list.append(
                    {
                        "usuario": usuario,
                        "atividades": atividades,
                        "total_usuario": total_usuario,
                    }
                )
            resposta[sistema] = {
                "usuarios": usuarios_list,
                "total_sistema": total_sistema,
            }

        return JsonResponse(resposta, safe=False)

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Erro na get_analise_por_sistema: {e}\n{tb}")
        return JsonResponse({"error": str(e), "traceback": tb}, status=500)
