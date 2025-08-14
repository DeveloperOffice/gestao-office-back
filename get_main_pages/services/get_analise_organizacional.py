from collections import defaultdict
from odbc_reader.services import fetch_data

def get_organizacional():
    query_sindicatos = """
    SELECT i_sindicatos, nome, mes_base
    FROM bethadba.fosindicatos
    """
    try:
        sindicatos_data = fetch_data(query_sindicatos)
        sindicatos = {row["i_sindicatos"]: {"nome": row["nome"], "mes_base": row["mes_base"]} for row in sindicatos_data}
    except Exception as e:
        return {"erro": f"Erro ao buscar sindicatos: {str(e)}"}

    query = """
        SELECT
            f.codi_emp,
            emp.nome_emp AS nome_empresa,
            r.demissao,
            f.i_empregados AS i_empregado,
            f.nome AS nome_empregado,
            f.i_sindicatos,
            COALESCE(a.novo_salario, f.salario) AS salario,

            -- Base/dias do aviso (traz se existir GRFC; senão 0)
            COALESCE(g.aviso_previo_base, 0) AS aviso_previo_base,

            /* ====== VALOR DO AVISO PRÉVIO NA RESCISÃO (classificação 24) ====== */
            CAST(
            COALESCE((
                SELECT SUM(MOV.VALOR_CAL)
                FROM BETHADBA.FOMOVTOSERV MOV
                JOIN BETHADBA.FOEVENTOS EVE
                ON EVE.I_EVENTOS = MOV.I_EVENTOS
                JOIN BETHADBA.FOPARMTO PARM
                ON PARM.CODI_EMP = f.codi_emp
                AND EVE.CODI_EMP = PARM.CODI_EMP_EVE
                WHERE MOV.I_CALCULOS = r.I_CALCULOS
                AND EVE.CLASSIFICACAO = 24
                AND (EVE.COMPOE_LIQUIDO = 1 OR EVE.APARECE_RECIBO = 'S')
                AND (
                        MOV.ORIGEM IN ('C','G','I')
                    OR (MOV.ORIGEM = 'F' AND PARM.MOV_FER_MES = 'S')
                )
            ), 0) AS DECIMAL(18,6)
            ) AS aviso_previo_valor,

            /* ====== 13º DA RESCISÃO (classificação 23) ====== */
            CAST(
            COALESCE((
                SELECT SUM(MOV.VALOR_CAL)
                FROM BETHADBA.FOMOVTOSERV MOV
                JOIN BETHADBA.FOEVENTOS EVE
                ON EVE.I_EVENTOS = MOV.I_EVENTOS
                JOIN BETHADBA.FOPARMTO PARM
                ON PARM.CODI_EMP = f.codi_emp
                AND EVE.CODI_EMP = PARM.CODI_EMP_EVE
                WHERE MOV.I_CALCULOS = r.I_CALCULOS
                AND EVE.CLASSIFICACAO = 23
                AND (EVE.COMPOE_LIQUIDO = 1 OR EVE.APARECE_RECIBO = 'S')
                AND (
                        MOV.ORIGEM IN ('C','G','I')
                    OR (MOV.ORIGEM = 'F' AND PARM.MOV_FER_MES = 'S')
                )   
            ), 0) AS DECIMAL(18,6)
            ) AS decimo_terceiro_rescisao,

            /* ====== 13º NORMAL (TP 51 + 52 no ano corrente) ====== */
            CAST(
            COALESCE((
                SELECT SUM(MOV.VALOR_CAL)
                FROM BETHADBA.FOMOVTOSERV MOV
                JOIN BETHADBA.FOEVENTOS EVE
                ON EVE.I_EVENTOS = MOV.I_EVENTOS
                JOIN BETHADBA.FOPARMTO PARM
                ON PARM.CODI_EMP = f.codi_emp
                AND EVE.CODI_EMP = PARM.CODI_EMP_EVE
                JOIN BETHADBA.FOBASESSERV BAS
                ON BAS.I_CALCULOS = MOV.I_CALCULOS
                WHERE BAS.CODI_EMP = f.CODI_EMP
                AND BAS.I_EMPREGADOS = f.I_EMPREGADOS
                AND BAS.TIPO_PROCESS IN (51, 52)
                AND BAS.RATEIO = 0
                AND YEAR(BAS.COMPETENCIA) = YEAR(CURRENT DATE)
                AND EVE.CLASSIFICACAO = 23
                AND (EVE.COMPOE_LIQUIDO = 1 OR EVE.APARECE_RECIBO = 'S')
                AND (
                        MOV.ORIGEM IN ('C','G','I')
                    OR (MOV.ORIGEM = 'F' AND PARM.MOV_FER_MES = 'S')
                )
            ), 0) AS DECIMAL(18,6)
            ) AS decimo_terceiro,

            /* ====== FÉRIAS (TP=60): remuneração + 1/3 + abono + 1/3 do abono (TOTAL) ====== */
            CAST(
            COALESCE((
                SELECT SUM(MOV.VALOR_CAL)
                FROM BETHADBA.FOMOVTOSERV MOV
                JOIN BETHADBA.FOBASESSERV BASF
                ON BASF.I_CALCULOS = MOV.I_CALCULOS
                JOIN BETHADBA.FOEVENTOS EVE
                ON EVE.I_EVENTOS = MOV.I_EVENTOS
                JOIN BETHADBA.FOPARMTO PARM
                ON PARM.CODI_EMP = f.codi_emp
                AND EVE.CODI_EMP = PARM.CODI_EMP_EVE
                WHERE BASF.CODI_EMP = f.CODI_EMP
                AND BASF.I_EMPREGADOS = f.I_EMPREGADOS
                AND BASF.TIPO_PROCESS = 60           -- todas as folhas de férias
                AND BASF.RATEIO = 0                  -- igual ao Recibo_ferias
                AND MOV.I_EVENTOS IN (3, 930, 931, 932)  -- remuneração + 1/3 + abono + 1/3 do abono
                AND (EVE.COMPOE_LIQUIDO = 1 OR EVE.APARECE_RECIBO = 'S')
                AND (
                        MOV.ORIGEM IN ('C','G','I')
                    OR (MOV.ORIGEM = 'F' AND PARM.MOV_FER_MES = 'S')
                )
                AND MOV.DATA        = BASF.COMPETENCIA
                AND MOV.TIPO_PROCES = BASF.TIPO_PROCESS
                AND MOV.RATEIO      = BASF.RATEIO
                AND MOV.I_SERVICOS  = BASF.I_SERVICOS
            ), 0) AS DECIMAL(18,6)
            ) AS valor_férias_com_adicional_33,

            /* ====== FOLHA MENSAL (TP=42) – última competência disponível por empregado ====== */
            CAST(COALESCE((
                SELECT SUM(B.PROVENTOS)
                FROM BETHADBA.FOBASESSERV B
                WHERE B.CODI_EMP = f.CODI_EMP
                AND B.I_EMPREGADOS = f.I_EMPREGADOS
                AND B.TIPO_PROCESS = 42
                AND B.COMPETENCIA = ult42.ULT_COMP_42
            ),0) AS DECIMAL(18,6)) AS proventos_mensal,

            CAST(COALESCE((
                SELECT SUM(B.DESCONTOS)
                FROM BETHADBA.FOBASESSERV B
                WHERE B.CODI_EMP = f.CODI_EMP
                AND B.I_EMPREGADOS = f.I_EMPREGADOS
                AND B.TIPO_PROCESS = 42
                AND B.COMPETENCIA = ult42.ULT_COMP_42
            ),0) AS DECIMAL(18,6)) AS descontos_mensal,

            CAST(COALESCE((
                SELECT SUM(B.PROVENTOS - B.DESCONTOS)
                FROM BETHADBA.FOBASESSERV B
                WHERE B.CODI_EMP = f.CODI_EMP
                AND B.I_EMPREGADOS = f.I_EMPREGADOS
                AND B.TIPO_PROCESS = 42
                AND B.COMPETENCIA = ult42.ULT_COMP_42
            ),0) AS DECIMAL(18,6)) AS liquido_mensal

        FROM bethadba.foempregados f

        /* última competência de TP=42 por empregado */
        LEFT JOIN (
            SELECT CODI_EMP, I_EMPREGADOS, MAX(COMPETENCIA) AS ULT_COMP_42
            FROM BETHADBA.FOBASESSERV
            WHERE TIPO_PROCESS = 42
            GROUP BY CODI_EMP, I_EMPREGADOS
        ) ult42
        ON ult42.CODI_EMP = f.CODI_EMP
        AND ult42.I_EMPREGADOS = f.I_EMPREGADOS

        /* pega 1 linha de GRFC por empregado (evita duplicar) */
        LEFT JOIN (
            SELECT codi_emp, i_empregados, MAX(aviso_previo_base) AS aviso_previo_base
            FROM bethadba.foguiagrfc
            GROUP BY codi_emp, i_empregados
        ) g
        ON g.codi_emp = f.codi_emp
        AND g.i_empregados = f.i_empregados

        /* rescisão mais recente por empregado */
        LEFT JOIN (
            SELECT codi_emp, i_empregados,
                MAX(i_calculos) AS i_calculos,
                MAX(demissao)  AS demissao
            FROM bethadba.forescisoes
            GROUP BY codi_emp, i_empregados
        ) r
        ON r.codi_emp = f.codi_emp
        AND r.i_empregados = f.i_empregados

        LEFT JOIN bethadba.geempre emp
        ON f.codi_emp = emp.codi_emp AND emp.stat_emp = 'A'

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
        folha_total_bruta = defaultdict(float)
        folha_total_liquida = defaultdict(float)
        empresas_nomes = {}

        meses_nomes = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
            7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }

        for row in raw_data:
            proventos = float(row.get("proventos_mensal") or 0)
            descontos = float(row.get("descontos_mensal") or 0)
            liquido   = float(row.get("liquido_mensal") or 0)

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

                "aviso_previo_base": row["aviso_previo_base"],
                "aviso_previo_valor": row["aviso_previo_valor"],

                "decimo_terceiro_rescisao": row["decimo_terceiro_rescisao"],
                "decimo_terceiro": row["decimo_terceiro"],
                "valor_férias_com_adicional_33": row["valor_férias_com_adicional_33"],

                # novos (folha do mês corrente - TP=42)
                "proventos_mensal": row["proventos_mensal"],
                "descontos_mensal": row["descontos_mensal"],
                "liquido_mensal": row["liquido_mensal"],

                "dissidio": nome_sindicato,
                "mes_base": mes_base
            })

            folha_total_bruta[row["codi_emp"]]  += proventos
            folha_total_liquida[row["codi_emp"]] += liquido

        return {
            "dados": [
                {
                    "codi_emp": codi_emp,
                    "nome_empresa": empresas_nomes.get(codi_emp, "Empresa Desconhecida"),
                    # por compatibilidade, mantenho "folha_mensal" = líquido do mês
                    "folha_mensal": round(folha_total_liquida[codi_emp], 2),
                    "folha_mensal_liquida": round(folha_total_liquida[codi_emp], 2),
                    "folha_mensal_bruta": round(folha_total_bruta[codi_emp], 2),
                    "empregados": agrupado[codi_emp],
                }
                for codi_emp in agrupado.keys()
            ]
        }

    except Exception as e:
        return {"erro": str(e)}
