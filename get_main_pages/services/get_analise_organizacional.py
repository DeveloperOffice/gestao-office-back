from collections import defaultdict
from odbc_reader.services import fetch_data

def get_organizacional():
    query_sindicatos = """
    SELECT
        i_sindicatos,
        nome,
        mes_base
    FROM bethadba.fosindicatos
    """

    try:
        sindicatos_data = fetch_data(query_sindicatos)
        sindicatos = {row["i_sindicatos"]: {"nome": row["nome"], "mes_base": row["mes_base"]} for row in sindicatos_data}
    except Exception as e:
        return {"erro": f"Erro ao buscar sindicatos: {str(e)}"}

    query = """
        SELECT
            g.codi_emp,
            emp.nome_emp AS nome_empresa,
            r.demissao,
            g.i_empregados AS i_empregado,
            f.nome AS nome_empregado,
            f.i_sindicatos,
            COALESCE(a.novo_salario, f.salario) AS salario,
            g.aviso_previo_base AS aviso_previo,

            /* ====== TROCA 1: 13º DA RESCISÃO (classificação 23 do cálculo da rescisão) ====== */
            CAST(
            COALESCE((
                SELECT SUM(MOV.VALOR_CAL)
                FROM BETHADBA.FOMOVTOSERV MOV
                JOIN BETHADBA.FOEVENTOS EVE
                    ON EVE.I_EVENTOS = MOV.I_EVENTOS
                JOIN BETHADBA.FOPARMTO PARM
                    ON PARM.CODI_EMP = g.codi_emp
                AND EVE.CODI_EMP = PARM.CODI_EMP_EVE
                WHERE MOV.I_CALCULOS = r.I_CALCULOS
                AND EVE.CLASSIFICACAO = 23
                AND MOV.ORIGEM IN ('C','G','I','F')
            ), 0) AS DECIMAL(18,6)
            ) AS decimo_terceiro_rescisao,

            /* ====== TROCA 2: 13º NORMAL NO ANO ATUAL (TIPO_PROCESS 51 + 52) ====== */
            CAST(
            COALESCE((
                SELECT SUM(MOV.VALOR_CAL)
                FROM BETHADBA.FOMOVTOSERV MOV
                JOIN BETHADBA.FOEVENTOS EVE
                    ON EVE.I_EVENTOS = MOV.I_EVENTOS
                JOIN BETHADBA.FOPARMTO PARM
                    ON PARM.CODI_EMP = g.codi_emp
                AND EVE.CODI_EMP = PARM.CODI_EMP_EVE
                JOIN BETHADBA.FOBASESSERV BAS
                    ON BAS.I_CALCULOS = MOV.I_CALCULOS
                WHERE BAS.CODI_EMP = f.CODI_EMP
                AND BAS.I_EMPREGADOS = f.I_EMPREGADOS
                AND BAS.TIPO_PROCESS IN (51, 52)
                AND BAS.RATEIO = 0
                AND YEAR(BAS.COMPETENCIA) = YEAR(CURRENT DATE)
                AND EVE.CLASSIFICACAO = 23
                AND MOV.ORIGEM IN ('C','G','I','F')
            ), 0) AS DECIMAL(18,6)
            ) AS decimo_terceiro,

            -- Cálculo do valor das férias (inclui 33% adicional e abono)
            COALESCE(fl.valor_ferias, 0) AS valor_ferias,

            -- Cálculo das férias (salário + 33% adicional + abono)
            CASE
                WHEN f.categoria IN (4, 5) AND f.carga_horaria_variavel = 1 THEN
                    f.salario
                ELSE
                    COALESCE(a.novo_salario, f.salario)
            END * 1.33 AS valor_férias_com_adicional_33

        FROM bethadba.foguiagrfc g
        LEFT JOIN bethadba.foempregados f 
            ON g.codi_emp = f.codi_emp AND g.i_empregados = f.i_empregados
        LEFT JOIN bethadba.forescisoes r 
            ON f.codi_emp = r.codi_emp AND f.i_empregados = r.i_empregados
        LEFT JOIN bethadba.geempre emp
            ON g.codi_emp = emp.codi_emp AND emp.stat_emp = 'A'
        LEFT JOIN (
            SELECT 
                codi_emp, 
                i_empregados,
                MAX(novo_salario) AS novo_salario  
            FROM bethadba.foaltesal
            GROUP BY codi_emp, i_empregados
        ) a
            ON f.codi_emp = a.codi_emp AND f.i_empregados = a.i_empregados
        LEFT JOIN (
            SELECT
                codi_emp,
                i_empregados,   
                SUM(COALESCE(valor_informado, valor_calculado)) AS valor_ferias
            FROM bethadba.foferias_lancamentos
            GROUP BY codi_emp, i_empregados
        ) fl
            ON f.codi_emp = fl.codi_emp AND f.i_empregados = fl.i_empregados
        WHERE f.admissao IS NOT NULL;

    """

    try:
        raw_data = fetch_data(query)
        agrupado = defaultdict(list)
        folha_total = defaultdict(float)
        empresas_nomes = {}

        meses_nomes = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
        7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }

        
        for row in raw_data:
            salario = float(row["salario"] or 0)            

            codigo_sindicato = row.get("i_sindicatos")
            sindicato_info = sindicatos.get(codigo_sindicato, {"nome": "SINDICATO DESCONHECIDO", "mes_base": None})
            nome_sindicato = sindicato_info["nome"]
            mes_base_num = sindicato_info["mes_base"]
            mes_base = meses_nomes.get(mes_base_num, "mês desconhecido")

            empresas_nomes[row["codi_emp"]] = row.get("nome_empresa", "Empresa Desconhecida")

            agrupado[row["codi_emp"]].append({
                "demissao_debug": row.get("demissao"),
                "i_empregado": row["i_empregado"],
                "nome_empregado": row.get("nome_empregado", "NOME DESCONHECIDO"),
                "salario": row["salario"],
                "aviso_previo": row["aviso_previo"],
                "decimo_terceiro_rescisao": row["decimo_terceiro_rescisao"],
                "decimo_terceiro": row["decimo_terceiro"],
                "valor_férias_com_adicional_33": row["valor_férias_com_adicional_33"],
                "dissidio": nome_sindicato,
                "mes_base": mes_base  
            })

            folha_total[row["codi_emp"]] += salario

        return {
            "dados": [
                {
                    "codi_emp": codi_emp,
                    "nome_empresa": empresas_nomes.get(codi_emp, "Empresa Desconhecida"),
                    "folha_mensal": round(folha_total[codi_emp], 2),
                    "empregados": agrupado[codi_emp],
                }
                for codi_emp, empregados in agrupado.items()
            ]
        }

    except Exception as e:
        return {"erro": str(e)}
