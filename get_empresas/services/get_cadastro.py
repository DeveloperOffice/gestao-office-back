from django.http import JsonResponse
from odbc_reader.services import fetch_data
from datetime import datetime, timedelta


def get_cadastros():
    try:
        query = """SELECT nome_emp, 
        cepe_emp, 
        cgce_emp, 
        ramo_emp, 
        codi_emp, 
        rleg_emp,
        dtinicio_emp,
        dcad_emp
        FROM bethadba.geempre WHERE stat_emp = 'A'"""
        result = fetch_data(query)
        return result
    except Exception as e:
        return {"error": str(e)}


def get_aniversariantes():
    try:
        empresas = get_cadastros()
        hoje = datetime.today()

        # Definir o intervalo do mês atual com 5 dias antes do primeiro e 5 dias após o último dia do mês
        primeiro_dia_mes = hoje.replace(day=1)
        ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=32)).replace(
            day=1
        ) - timedelta(days=1)

        # Intervalos adicionais de 5 dias antes e 5 dias depois
        intervalo_inicial = primeiro_dia_mes - timedelta(
            days=5
        )  # 5 dias antes do primeiro dia
        intervalo_final = ultimo_dia_mes + timedelta(
            days=5
        )  # 5 dias depois do último dia

        aniversariante_cadastro = []
        aniversariante_inicio_atividades = []

        vistos = set()

        for emp in empresas:
            codi_emp = emp.get("codi_emp")
            nome = emp.get("nome_emp")
            cnpj = emp.get("cgce_emp") or ""
            data_cadastro = emp.get("dcad_emp")
            data_inicio = emp.get("dtinicio_emp")

            if codi_emp in vistos:
                continue
            vistos.add(codi_emp)

            # Mantendo a conversão das datas para strings
            data_cadastro_str = (
                data_cadastro.strftime("%Y-%m-%d") if data_cadastro else None
            )
            data_inicio_str = data_inicio.strftime("%Y-%m-%d") if data_inicio else None

            # Aniversário de cadastro dentro do intervalo (5 dias antes do primeiro até 5 dias após o último dia do mês)
            if data_cadastro:
                try:
                    aniversario = datetime(
                        hoje.year, data_cadastro.month, data_cadastro.day
                    )
                    if intervalo_inicial <= aniversario <= intervalo_final:
                        aniversariante_cadastro.append(
                            {
                                "codi_emp": codi_emp,
                                "nome": nome,
                                "cnpj": cnpj,
                                "data_cadastro": data_cadastro_str,
                                "data_inicio_atividades": data_inicio_str,
                            }
                        )
                except ValueError:
                    pass  # Pula datas inválidas, como 29/02 em ano não bissexto

            # Aniversário de início de atividades dentro do intervalo
            if data_inicio:
                try:
                    aniversario = datetime(
                        hoje.year, data_inicio.month, data_inicio.day
                    )
                    if intervalo_inicial <= aniversario <= intervalo_final:
                        aniversariante_inicio_atividades.append(
                            {
                                "codi_emp": codi_emp,
                                "nome": nome,
                                "cnpj": cnpj,
                                "data_cadastro": data_cadastro_str,
                                "data_inicio_atividades": data_inicio_str,
                            }
                        )
                except ValueError:
                    pass

        return {
            "aniversarios": {
                "aniversariante_cadastro": {
                    "total": len(aniversariante_cadastro),
                    "empresas": aniversariante_cadastro,
                },
                "aniversariante_inicio_atividades": {
                    "total": len(aniversariante_inicio_atividades),
                    "empresas": aniversariante_inicio_atividades,
                },
            }
        }

    except Exception as e:
        return {"error": str(e)}
