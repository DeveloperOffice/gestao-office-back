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

      /* ====== AVISO PRÉVIO (BASE / DIAS) — da MESMA rescisão ====== */
      COALESCE(g.aviso_previo_base, 0) AS aviso_previo_base,

      /* ====== VALOR DO AVISO PRÉVIO (classificação 24) — cálculo da rescisão ====== */
      CAST(
        COALESCE((
          SELECT SUM(MOV.VALOR_CAL)
            FROM BETHADBA.FOMOVTOSERV MOV
            JOIN BETHADBA.FOEVENTOS EVE
              ON EVE.I_EVENTOS = MOV.I_EVENTOS
            JOIN BETHADBA.FOPARMTO PARM
              ON PARM.CODI_EMP = f.codi_emp
            AND EVE.CODI_EMP = PARM.CODI_EMP_EVE
          WHERE MOV.I_CALCULOS    = r.I_CALCULOS
            AND EVE.CLASSIFICACAO = 24
            AND (
                  MOV.ORIGEM IN ('C','I')
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
          WHERE MOV.I_CALCULOS    = r.I_CALCULOS
            AND EVE.CLASSIFICACAO = 23
            AND (
                  MOV.ORIGEM IN ('C','I')
                OR (MOV.ORIGEM = 'F' AND PARM.MOV_FER_MES = 'S')
            )
        ), 0) AS DECIMAL(18,6)
      ) AS decimo_terceiro_rescisao,

      /* ====== 13º NORMAL (TP 51 + 52 no ano da competência de referência) ====== */
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
            AND YEAR(BAS.COMPETENCIA) = YEAR(tcomp.COMP_ANTERIOR)
            AND EVE.CLASSIFICACAO = 23
            AND (
                  MOV.ORIGEM IN ('C','I')
                OR (MOV.ORIGEM = 'F' AND PARM.MOV_FER_MES = 'S')
            )
        ), 0) AS DECIMAL(18,6)
      ) AS decimo_terceiro,

      /* ====== FÉRIAS (TP=60): ÚLTIMAS férias do empregado ====== */
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
            AND BASF.TIPO_PROCESS = 60
            AND BASF.RATEIO = 0
            AND BASF.COMPETENCIA = (
                SELECT MAX(B2.COMPETENCIA)
                  FROM BETHADBA.FOBASESSERV B2
                WHERE B2.CODI_EMP     = f.CODI_EMP
                  AND B2.I_EMPREGADOS = f.I_EMPREGADOS
                  AND B2.TIPO_PROCESS = 60
                  AND B2.RATEIO       = 0
            )10.65 
            AND MOV.I_EVENTOS IN (3, 930, 931, 932)  -- (inclua 34 se quiser férias em dobro)
            AND (
                  MOV.ORIGEM IN ('C','I')
                OR (MOV.ORIGEM = 'F' AND PARM.MOV_FER_MES = 'S')
            )
            AND MOV.DATA        = BASF.COMPETENCIA
            AND MOV.TIPO_PROCES = BASF.TIPO_PROCESS
            AND MOV.RATEIO      = BASF.RATEIO
            AND MOV.I_SERVICOS  = BASF.I_SERVICOS
        ), 0) AS DECIMAL(18,6)
      ) AS valor_férias_com_adicional_33,

      /* ====== FOLHA MENSAL (TP=42) — última competência antes do mês atual (via tcomp) ====== */
      CAST(COALESCE((
          SELECT SUM(B.PROVENTOS)
            FROM BETHADBA.FOBASESSERV B
          WHERE B.CODI_EMP = f.CODI_EMP
            AND B.I_EMPREGADOS = f.I_EMPREGADOS
            AND B.TIPO_PROCESS = 42
            AND B.COMPETENCIA = tcomp.COMP_ANTERIOR
      ),0) AS DECIMAL(18,6)) AS proventos_mensal,

      CAST(COALESCE((
          SELECT SUM(B.DESCONTOS)
            FROM BETHADBA.FOBASESSERV B
          WHERE B.CODI_EMP = f.CODI_EMP
            AND B.I_EMPREGADOS = f.I_EMPREGADOS
            AND B.TIPO_PROCESS = 42
            AND B.COMPETENCIA = tcomp.COMP_ANTERIOR
      ),0) AS DECIMAL(18,6)) AS descontos_mensal,

      CAST(COALESCE((
          SELECT SUM(B.PROVENTOS - B.DESCONTOS)
            FROM BETHADBA.FOBASESSERV B
          WHERE B.CODI_EMP = f.CODI_EMP
            AND B.I_EMPREGADOS = f.I_EMPREGADOS
            AND B.TIPO_PROCESS = 42
            AND B.COMPETENCIA = tcomp.COMP_ANTERIOR
      ),0) AS DECIMAL(18,6)) AS liquido_mensal,

      -- debug
      tcomp.COMP_ANTERIOR AS competencia_folha

  FROM bethadba.foempregados f

  /* última competência REAL de folha mensal (TP=42) antes do mês atual */
  LEFT JOIN (
      SELECT 
          b.codi_emp,
          b.i_empregados,
          MAX(b.competencia) AS COMP_ANTERIOR
        FROM bethadba.fobasesserv b
      WHERE b.tipo_process = 42
        AND b.competencia < CAST( DATEADD(day, 1 - DAY(CURRENT DATE), CURRENT DATE) AS DATE )
      GROUP BY b.codi_emp, b.i_empregados
  ) tcomp
    ON tcomp.codi_emp = f.codi_emp
  AND tcomp.i_empregados = f.i_empregados

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

  /* >>> AVISO PRÉVIO (base) amarrado à MESMA rescisão (mesmo I_CALCULOS) <<< */
  LEFT JOIN bethadba.foguiagrfc g
        ON g.codi_emp     = f.codi_emp
        AND g.i_empregados = f.i_empregados
        AND g.i_calculos   = r.i_calculos

  LEFT JOIN bethadba.geempre emp
    ON f.codi_emp = emp.codi_emp
  AND emp.stat_emp = 'A'

  LEFT JOIN (
      SELECT 
          codi_emp, 
          i_empregados,
          MAX(novo_salario) AS novo_salario  
        FROM bethadba.foaltesal
      GROUP BY codi_emp, i_empregados
  ) a
    ON f.codi_emp = a.codi_emp
  AND f.i_empregados = a.i_empregados

  LEFT JOIN (
      SELECT  
          codi_emp,
          i_empregados,   
          SUM(COALESCE(valor_informado, valor_calculado)) AS valor_ferias
        FROM bethadba.foferias_lancamentos
      GROUP BY codi_emp, i_empregados
  ) fl
    ON f.codi_emp = fl.codi_emp
  AND f.i_empregados = fl.i_empregados

  WHERE f.admissao IS NOT NULL;


    """

    try:
        raw_data = fetch_data(query)
        agrupado = defaultdict(list)
        folha_total_bruta = defaultdict(float)
        folha_total_liquida = defaultdict(float)
        folha_total_descontos = defaultdict(float)
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
                "valor_férias_com_adiciona l_33": row["valor_férias_com_adicional_33"],

                # novos (folha do mês corrente - TP=42)
                "proventos_mensal": round(proventos, 2),
                "descontos_mensal": round(descontos, 2),
                "liquido_mensal": round(liquido, 2),


                "dissidio": nome_sindicato,
                "mes_base": mes_base
            })

            folha_total_bruta[row["codi_emp"]]  += proventos
            folha_total_liquida[row["codi_emp"]] += liquido
            folha_total_descontos[row["codi_emp"]] += descontos

        return {
            "dados": [
                {
                    "codi_emp": codi_emp,
                    "nome_empresa": empresas_nomes.get(codi_emp, "Empresa Desconhecida"),
                    "folha_mensal": round(folha_total_liquida[codi_emp], 2),
                    "folha_mensal_liquida": round(folha_total_liquida[codi_emp], 2),
                    "folha_mensal_bruta": round(folha_total_bruta[codi_emp], 2),
                    "folha_mensal_descontos": round(folha_total_descontos[codi_emp], 2),
                    "empregados": agrupado[codi_emp],
                }
                for codi_emp in agrupado.keys()
            ]
        }

    except Exception as e:
        return {"erro": str(e)}
