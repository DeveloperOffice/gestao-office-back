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


from datetime import datetime, timedelta

from datetime import datetime, timedelta


def get_aniversariantes():
    try:
        empresas = get_cadastros()
        hoje = datetime.today()

        aniversariante_cadastro = []
        aniversariante_inicio_atividades = []

        vistos = set()

        for emp in empresas:
            codi_emp = emp.get("codi_emp")
            nome = emp.get("nome_emp")
            cnpj = emp.get("cgce_emp")
            data_cadastro = emp.get("dcad_emp")
            data_inicio = emp.get("dtinicio_emp")

            if codi_emp in vistos:
                continue
            vistos.add(codi_emp)

            data_cadastro_str = (
                data_cadastro.strftime("%Y-%m-%d") if data_cadastro else None
            )
            data_inicio_str = data_inicio.strftime("%Y-%m-%d") if data_inicio else None

            # Aniversário de cadastro nos próximos 30 dias
            if data_cadastro:
                try:
                    aniversario = datetime(
                        hoje.year, data_cadastro.month, data_cadastro.day
                    )
                    delta_dias = (aniversario.date() - hoje.date()).days
                    if 0 <= delta_dias <= 30:
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
                    pass  # pula datas inválidas como 29/02 em ano não bissexto

            # Aniversário de início de atividades nos próximos 30 dias
            if data_inicio:
                try:
                    aniversario = datetime(
                        hoje.year, data_inicio.month, data_inicio.day
                    )
                    delta_dias = (aniversario.date() - hoje.date()).days
                    if 0 <= delta_dias <= 30:
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
