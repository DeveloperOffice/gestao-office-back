from odbc_reader.services import fetch_data

def get_organizacional():
    query = """
    SELECT 
        FOGUIAGRFC.CODI_EMP,  -- Selecionando o código da empresa
        SUM(COALESCE(FOGUIAGRFC.RESC_VALOR, 0.00)) AS RESC_VALOR,  -- Somando o valor de rescisão por empresa
        SUM(COALESCE(FOBASESSERV.BASE_FGTS, 0.00)) AS BASE_FGTS  -- Somando o valor de FGTS por empresa
    FROM 
        BETHADBA.FOGUIAGRFC AS FOGUIAGRFC
    LEFT JOIN 
        BETHADBA.FOBASESSERV AS FOBASESSERV
    ON 
        FOGUIAGRFC.CODI_EMP = FOBASESSERV.CODI_EMP
    WHERE 
        FOGUIAGRFC.I_EMPREGADOS = FOBASESSERV.I_EMPREGADOS
        AND FOBASESSERV.COMPETENCIA = '2024-12-01'  -- Ajuste conforme necessário
    GROUP BY 
        FOGUIAGRFC.CODI_EMP  -- Agrupando os resultados por código da empresa
    """
    try:
        result = fetch_data(query)  # Executando a consulta
        return {"dados": result}  # Retornando os dados
    except Exception as e:
        return {"erro": str(e)}  # Retorna o erro caso ocorra
