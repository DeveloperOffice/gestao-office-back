from odbc_reader.services import fetch_data

def get_lista_contadores():
    try:
        query = """SELECT
                GeContador.codi_con AS codi_cont,
                GeContador.nome_con,
                GeContador.cpfc_con AS cpf,
                GeContador.categoria_con AS categoria
                FROM bethadba.GeContador"""
                
        result = fetch_data(query)
        return result
    except Exception as e:
        return {"error": str(e)}