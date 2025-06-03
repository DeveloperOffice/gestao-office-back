from odbc_reader.services import fetch_data


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
