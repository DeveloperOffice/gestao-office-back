from odbc_reader.services import fetch_data


def get_fiscal(start_date, end_date):
    querySaidas = f"""
    SELECT
        efsaidas.codi_cli AS cliente,
        efclientes.nomr_cli AS nome_cliente,
        efsaidas.codi_emp AS empresa,
        geempre.nome_emp AS nome_empresa,
        geempre.cgce_emp AS cnpj,
        efsaidas.sigl_est AS UF,
        efsaidas.dsai_sai AS data,
        efsaidas.vcon_sai AS valor,
        efsaidas.cancelada_sai AS cancelada

    FROM bethadba.efsaidas
    INNER JOIN bethadba.geempre ON efsaidas.codi_emp = geempre.codi_emp
    INNER JOIN bethadba.efclientes ON efsaidas.codi_cli = efclientes.codi_cli AND efclientes.codi_emp = efsaidas.codi_emp
    WHERE efsaidas.dsai_sai BETWEEN '{start_date}' AND '{end_date}'
    """
    queryServicos = f"""
    SELECT
        efservicos.codi_cli AS cliente,
        efclientes.nomr_cli AS nome_cliente,
        efservicos.codi_emp AS empresa,
        geempre.nome_emp AS nome_empresa,
        geempre.cgce_emp AS cnpj,
        efservicos.sigl_est AS UF,
        efservicos.dser_ser AS data,
        efservicos.vcon_ser AS valor,
        efservicos.cancelada_ser AS cancelada

    FROM bethadba.efservicos
    INNER JOIN bethadba.geempre ON efservicos.codi_emp = geempre.codi_emp
    INNER JOIN bethadba.efclientes ON efservicos.codi_cli = efclientes.codi_cli AND efclientes.codi_emp = efservicos.codi_emp
    WHERE efservicos.dser_ser BETWEEN '{start_date}' AND '{end_date}'
    """

    queryEntradas = f"""
    SELECT
        efentradas.codi_for AS fornecedor,
        effornece.nomr_for AS nome_fornecedor,
        efentradas.codi_emp AS empresa,
        geempre.nome_emp AS nome_empresa,
        geempre.cgce_emp AS cnpj,
        effornece.cepe_for AS CEP,
        efentradas.dent_ent AS data,
        efentradas.vcon_ent AS valor

    FROM bethadba.efentradas
    INNER JOIN bethadba.geempre ON efentradas.codi_emp = geempre.codi_emp
    INNER JOIN bethadba.effornece ON efentradas.codi_for = effornece.codi_for AND effornece.codi_emp = efentradas.codi_emp
    WHERE efentradas.dent_ent BETWEEN '{start_date}' AND '{end_date}'
    """

    resultSaidas = fetch_data(querySaidas)
    resultServicos = fetch_data(queryServicos)
    resultEntradas = fetch_data(queryEntradas)

    return {
        "saidas": resultSaidas,
        "servicos": resultServicos,
        "entradas": resultEntradas,
    }
