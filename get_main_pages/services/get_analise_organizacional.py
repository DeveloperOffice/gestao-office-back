from odbc_reader.services import fetch_data

def get_organizacional():
    query = """
    SELECT
        g.codi_emp,
        g.i_empregados,
        g.aviso_previo_base,
        f.salario AS salario_inicial,
        a.novo_salario
    FROM
        bethadba.foguiagrfc g
    LEFT JOIN
        bethadba.foempregados f
        ON g.codi_emp = f.codi_emp AND g.i_empregados = f.i_empregados
    LEFT JOIN
        (
            SELECT 
                codi_emp, 
                i_empregados, 
                MAX(novo_salario) AS novo_salario  
            FROM 
                bethadba.foaltesal
            GROUP BY 
                codi_emp, i_empregados
        ) a
        ON f.codi_emp = a.codi_emp AND f.i_empregados = a.i_empregados;

    """
    try:
        result = fetch_data(query)
        return {"dados": result}
    except Exception as e:
        return {"erro": str(e)}
