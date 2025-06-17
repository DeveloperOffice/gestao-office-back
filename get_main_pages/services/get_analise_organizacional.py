from odbc_reader.services import fetch_data

def get_organizacional():
    query = """
        SELECT
        FOVREMUNERACAO_MENSAL.CODI_EMP,
        FOVREMUNERACAO_MENSAL.I_EMPREGADOS,
        FOVREMUNERACAO_MENSAL.VALOR_MES,
        FOVREMUNERACAO_MENSAL.VALOR_DISSIDIO_COLETIVO_RESCISAO

        FROM bethadba.FOVREMUNERACAO_MENSAL
    """

    result = fetch_data(query)
    return {"dados": result}    