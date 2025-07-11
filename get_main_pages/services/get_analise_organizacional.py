from collections import defaultdict
from odbc_reader.services import fetch_data

def get_organizacional():
    query = """
    SELECT
        g.codi_emp,
        r.demissao,
        g.i_empregados AS i_empregado,

        CASE 
            WHEN a.novo_salario IS NOT NULL AND a.novo_salario <> f.salario
            THEN a.novo_salario  
            ELSE f.salario
        END AS salario,

        g.aviso_previo_base AS aviso_previo,

        CASE 
            WHEN r.demissao IS NOT NULL AND r.demissao <= CURRENT DATE THEN 
                ROUND(
                    (
                        CASE 
                            WHEN a.novo_salario IS NOT NULL AND a.novo_salario <> f.salario
                            THEN a.novo_salario  
                            ELSE f.salario
                        END / 12.0
                    ) * (
                        DATEDIFF(month, 
                            CASE 
                                WHEN f.admissao > CAST(STR(YEAR(r.demissao)) || '-01-01' AS DATE)
                                THEN f.admissao 
                                ELSE CAST(STR(YEAR(r.demissao)) || '-01-01' AS DATE)
                            END, 
                            r.demissao
                        ) + CASE WHEN DAY(r.demissao) >= 15 THEN 1 ELSE 0 END
                    ),
                    2
                )
            ELSE 0
        END AS decimo_terceiro_rescisao,

        CASE 
            WHEN r.demissao IS NULL OR r.demissao > CURRENT DATE THEN
                ROUND(
                    (
                        CASE 
                            WHEN a.novo_salario IS NOT NULL AND a.novo_salario <> f.salario
                            THEN a.novo_salario  
                            ELSE f.salario
                        END / 12.0
                    ) * (
                        DATEDIFF(month, 
                            CASE 
                                WHEN f.admissao > CAST(STR(YEAR(CURRENT DATE)) || '-01-01' AS DATE)
                                THEN f.admissao 
                                ELSE CAST(STR(YEAR(CURRENT DATE)) || '-01-01' AS DATE)
                            END,
                            CURRENT DATE
                        ) + CASE WHEN DAY(CURRENT DATE) >= 15 THEN 1 ELSE 0 END
                    ),
                    2
                )
            ELSE 0
        END AS decimo_terceiero,

        COALESCE(fl.valor_ferias, 0) AS valor_ferias

    FROM bethadba.foguiagrfc g
    LEFT JOIN bethadba.foempregados f 
        ON g.codi_emp = f.codi_emp AND g.i_empregados = f.i_empregados
    LEFT JOIN bethadba.forescisoes r 
        ON f.codi_emp = r.codi_emp AND f.i_empregados = r.i_empregados
    LEFT JOIN (
        SELECT 
            codi_emp, 
            i_empregados, 
            MAX(novo_salario) AS novo_salario  
        FROM bethadba.foaltesal
        GROUP BY codi_emp, i_empregados
    ) a 
        ON f.codi_emp = a.codi_emp AND f.i_empregados = a.i_empregados

    -- Férias pagas
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

        for row in raw_data:
            codi_emp = row["codi_emp"]
            salario = float(row["salario"]) if row["salario"] else 0

            empregado = {
                "demissao_debug": row.get("demissao"),
                "i_empregado": row["i_empregado"],
                "salario": row["salario"],
                "aviso_previo": row["aviso_previo"],
                "decimo_terceiro_rescisao": row["decimo_terceiro_rescisao"],
                "decimo_terceiro": row["decimo_terceiro"],
                "valor_ferias": row["valor_ferias"]
            }

            agrupado[codi_emp].append(empregado)
            folha_total[codi_emp] += salario

        resultado_formatado = []
        for codi_emp, empregados in agrupado.items():
            resultado_formatado.append({
                "codi_emp": codi_emp,
                "folha_mensal": round(folha_total[codi_emp], 2),
                "empregados": empregados
            })

        return {"dados": resultado_formatado}

    except Exception as e:
        return {"erro": str(e)}
