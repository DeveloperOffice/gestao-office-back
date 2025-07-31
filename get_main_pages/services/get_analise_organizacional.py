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
        
        CASE 
            WHEN r.demissao IS NOT NULL AND r.demissao <= CURRENT DATE THEN 
                ROUND((COALESCE(a.novo_salario, f.salario) / 12.0) * (
                    DATEDIFF(month, 
                        CASE 
                            WHEN f.admissao > DATE(YEAR(r.demissao) || '-01-01') THEN f.admissao
                            ELSE DATE(YEAR(r.demissao) || '-01-01')
                        END, 
                        r.demissao
                    ) + CASE WHEN DAY(r.demissao) >= 15 THEN 1 ELSE 0 END
                ), 2)
            ELSE 0
        END AS decimo_terceiro_rescisao,
        CASE 
            WHEN r.demissao IS NULL OR r.demissao > CURRENT DATE THEN
                ROUND((COALESCE(a.novo_salario, f.salario) / 12.0) * (
                    DATEDIFF(month, 
                        CASE 
                            WHEN f.admissao > DATE(YEAR(CURRENT DATE) || '-01-01') THEN f.admissao
                            ELSE DATE(YEAR(CURRENT DATE) || '-01-01')
                        END,
                        CURRENT DATE
                    ) + CASE WHEN DAY(CURRENT DATE) >= 15 THEN 1 ELSE 0 END
                ), 2)
            ELSE 0
        END AS decimo_terceiro,

        COALESCE(fl.valor_ferias, 0) AS valor_ferias

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
        )  a
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
        1: "janeiro", 2: "feveiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
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
                "valor_ferias": row["valor_ferias"],
                "dissidio": nome_sindicato,
                "mes_base":  mes_base  
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
