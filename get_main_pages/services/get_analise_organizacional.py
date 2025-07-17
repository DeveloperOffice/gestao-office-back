from collections import defaultdict
from odbc_reader.services import fetch_data

# Dicionário simplificado de sindicatos
SINDICATOS = {
    2: "SINDICATO DOS EMPREGADOS NO COMERCIO DE FORTALEZA",
    4: "STI METAL DE MARACANAU - CE",
    1: "SINDICATO DOS COMERCIARIOS",
    29: "SIND DOS TRAB NAS IND DO VESTUARIO E CALÇADOS MARAN",
    32: "SINDICATO DE HOTEIS RESTAURANTES, BARES E SIMILARES DO",
    41: "SINDVIGILANTES - SINDICATO DOS VIGILANTES DO ESTADO DO",
    62: "SINDICATO DOS TRAB NO COM MIN DERV PETRO DO EST CE",
    63: "SINDICATO DO COMERCIO DE CRATEÚS",
    93: "SINDICATO DOS EMPREGADOS EM EDIFICIOS DE SALVADOR",
    94: "SINDICATO DOS ADMINISTRADORES NO ESTADO DE MINAS GE",
    95: "SIMEC",
    113: "SIND DOS TRAB NA IND DA CONST E DA MADEIRA NO EST DA E",
    116: "SINDICATO DA CONST CIVIL NO EST DO CE",
    120: "SIND DAS IND. GRAFICAS NO EST.CEARA",
    133: "SINDICATO NO COM",
    134: "SINDICATO DOS EMPREGADOS NO COMERCIO DAS CIDADES D",
    137: "FED DOS TRAB NAS IND DO ESTADO DO RIO GRANDE DO NOR",
    138: "SIND EMPREG. EM POSTOS DE SERV COMB E DERIV DE PETR",
    149: "SIND DOS EMPREGADOS NO COMERCIO NO EST DO ESP SANT",
    150: "SINDIRESTCE",
    151: "SINDICATO DOS EMPREGADOS NO COMERCIO DE MOSSORO",
    170: "SINTRAMICO - SIND. EMPREG. COM MIN.DER. PETROLEO",
    176: "SIND DOS ENFERMEIROS DO EST DO CE",
    182: "SINDTRABTRANSPRODOVCEARA",
    187: "SINDPAN SINDICATO IND PANIFICACAO CE",
    188: "FETRACE",
    205: "SINTEC-SIND.TRAB DE ENTID.CLASSE NO ECE",
    243: "SINTRAHORTUGA - SIND.COM.HOT.BARES REST.E SIMILARES A",
    259: "NAO TEM SIND. DE DOMESTICO",
    260: "SIND DOS EMPREGADOS NO COM DE MARACANAU, MARANGUAP",
    262: "SINDICATO DOS TRAB NAS IND DE CONFECÇÕES DE ROUPAS DE CAL",
    266: "SIND OFIC. ALFA COST E TRAB NAS IND DE CONF DE ROUP EM C",
    283: "OAB - ORDEM DOS ADVOGADOS DO BRASIL-CE",
    295: "CLT",
    299: "FED TRAB IND E LAVANDERIAS EST CE",
    300: "STI CONFECCOES DE HORIZONTE E PACAJUS",
    303: "SIND DOS CONTABILISTAS DO CE CAUCAIA",
    307: "FED. TRAB. IND.CONST.CIV.IND.PARNAIBA",
    430: "(RESTAURANTE) SIND. INTERM. TRAB. C. HOTEL. S. TUR. H CE",
    456: "SINDELETRO - SINDICATO DOS ELETRICITARIOS DE FORTALEZ",
    460: "SINTEPAMEPE",
    463: "SIND DO COMERCIO VAREJISTA DE PACAJUS",
    464: "SINDICATO DOS TRAB. NAS IND. DA CONST. CIVIL",
    465: "FETRACE - FEDERAÇÃO DO COMERCIO EST CE",
    466: "SIND DOS EMPASSEIO E CONS LOC ADM IMMOV",
    467: "FENEPOSPETRO-FEDERAÇÃO NACIONAL DOS EMPR",
    468: "SINTRAHOTRUH - SIND TRAB HOTELEIROS E RESTAURANTES",
    469: "SIND RADIÁLISTAS E PUBLICITAR.DO CEARÁ",
    470: "SIND OFICIAIS ALF.COSTURE. E TRAB.ROUP.FOR.",
    471: "SIND.TRAB. NO COM.DO EST. CEARA E PIAUI",
    472: "SIND EMPREG.EM ESTAB.DE SERV DE SAUDE CE",
    473: "SIND DOS TÉC AUX EM RADIOLOGIA DO CE",
    474: "SIND METALURG.MECE MAT.ELET.EST.CEAR",
    475: "SINDICATO DOS FARMACÊUTICOS DO CEARÁ",
    476: "FETICOMED FED TRAB IND CONST MOB EST CE",
    477: "SIND.DOS TRAB.NA IND.CONF.FEM. E MODA-IND-SINDICONE",
    478: "SIND DAS EMPRESAS COM.VENDA ADM IMOV EDIF CONDM RES",
    479: "SEDITTEC-SIND DOS EMP DES TEC TECNOL EST",
    480: "STI DA CONST.E DO MOB DO MEDIO PARNAIBA",
    481: "SIESCON CE",
    483: "SIND DOS EMPREG NO COM JUAZEIRO DO NORTE",
    484: "SENGE SINDICATO ENGENHEIROS DO EST-CEARÁ",
    485: "SINDICATO DOS TRAB. TRANSP. RODOV. CEARÁ",
    486: "SINDGEL-CE",
    487: "FED. TRAB. INDUST CONST CIV JUAZ.DO NORTE",
    488: "SIND TRAB IND EXT BENEF SAL MÁRMORE ROCH",
    490: "FEDERAÇÃO COM DE BENS E SERV TUR EST PI",
    500: "SINTIGRACE",
    502: "STI CIMENTO CAL E GESSO DE FORTALEZA",
    507: "SIND C.V.DERIV.PETROLEO DO EST DO CEARA",
    508: "SINDICATO DAS IND.DE FRIO E PESCA EST CE",
    510: "SINDUSCON-SIND NA IND DA CONST CIVIL CE",
    511: "SINDICATO DOS TRABALHADORES NO COMERCIO HOTELEIRO",
    513: "SIND. DOS AUXILIARES DE ADM. ESCOLAR CE",
    514: "SINDICATO DOS PROFESSORES DO CEARA",
    516: "SEM CÓDIGO",
    519: "SIND. DO COM. ATACADISTA DE GÊNEROS ALIM",
    526: "SIND TRAB PROC DADOS,SERV INFORM SIMIL CE",
    527: "FEDERAÇÃO DAS INDUSTRIAS DO ESTADO CE",
    535: "SINTEPAV-CE SIND.TRAB.CONST.CIVIL PESADA",
    536: "STI PANIF CONF MASSAS ALIM.BISCO DO CEAR",
    545: "SINDICATO DOS CABELEIREIROS",
    548: "SINDICATO DOS TRAB. NAS INDUSTRIAS QUIMIC",
    570: "SIND.TRAB.IND.DOCES CONSERVAS ESTADO CE",
    572: "SINDICATO.SIND.TEC.AUX.OT.TRAB.IND.METAL",
    578: "SINDICATO DOS CONTABILISTAS DO ESTADO DO CEARÁ - SIND",
    581: "SIND DOS TRAB EM TRAN ROD DO EST DO SERG",
    587: "SIND REST BARES E SEM SAZONA MET FORT",
    629: "SINDICATO DOS EMPREGADOS NO COMÉRCIO DE FORTALEZA",
    731: "FETRACE - FEDERAÇÃO DOS TRABALHADORES NO COMÉRCIO",
    734: "SINDICATO DAS COSTUREIRAS DO ESTADO DO CEARA",
    753: "SINDICATO DOS TRABAL NAS IND DE PAPEL E PAPELÃO DE PETEC",
    758: "CLT",
    763: "SINGEECAS",
    1860: "SINDICATO DOS EMPREGADOS NO COMERCIO DE FORTALEZA",
    1861: "STI METAL DE MARACANAU - CE",
    1863: "SIND DOS TRAB NAS IND DE CONFECÇÃO FEMININA DE FORTALEZA",
    1864: "SINDSAÚDE",
    1865: "SIND DOS REPRESENTANTES COM DO EST CE",
    1866: "FEDERACAO DO COMERCIO DO ESTADO DO CEARA",
    1867: "FED TRAB COM E SERVICOS EST CE",
    1870: "SIND DOS ESTABELECIM DE SAUDE DO EST",
    1877: "SINDGEL-CE",
    1881: "SINDICATO DOS ARTESAOS",
    1882: "SEM CODIGO",
    1886: "SIND DOS TRAB NAS IND DO VESTUÁRIO E CALÇADOS MARANH",
    1890: "SINTICONF",
    1891: "SIND INTER. MUN. TRAB. COM. HOTELEIROS SIM. TUR. HOSP E",
    1898: "SINDVIGILANTES - SINDICATO DOS VIGILANTES DO ESTADO DO",
    1906: "SIND TRAB IND CONST CIVIL FORTALEZA",
    1911: "SIND. DA IND. DA CONSTRUÇÃO CIVIL DO EST. CE",
    1958: "SIND.DOS ELETRICITÁRIOS DO CEARA",
    2005: "SIND DOS EMPREGADOS NO COM DE MARACANAU, MARANGUAP",
    2007: "SINDIRESTCE",
    2033: "SIND DOS ENFERMEIROS DO EST DO CE",
    2056: "SINDPOSTO - SIND EMP POSTOS DE SERVICOS DE COMBUS",
    2102: "SIND DOS EMP NO COM DE CAUCAIA E MUN DE PENT APU GEN",
    2119: "SIND DOS TRAB NAS IND DE CONFECÇÕES DE ROUPAS DE CAL",
    2617: "SIND DOS TRAB NO COM HOT. BARES, REST E SIMIL, TURIS E H",
    2618: "SINDIMOTOOS - CE",
    2675: "SIND. DA IND. DA CONSTRUÇÃO CIVIL DO EST. CE",
    3381: "SIND DOS TRAB NO COM HOT. BARES, REST E SIMIL TURIS E H"
}


def get_organizacional():
    query = """
    SELECT
        g.codi_emp,
        r.demissao,
        g.i_empregados AS i_empregado,
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

        for row in raw_data:
            salario = float(row["salario"] or 0)
            codigo_sindicato = row.get("i_sindicatos")
            nome_sindicato = SINDICATOS.get(codigo_sindicato, "SINDICATO DESCONHECIDO")

            agrupado[row["codi_emp"]].append({
                "demissao_debug": row.get("demissao"),
                "i_empregado": row["i_empregado"],
                "salario": row["salario"],
                "aviso_previo": row["aviso_previo"],
                "decimo_terceiro_rescisao": row["decimo_terceiro_rescisao"],
                "decimo_terceiro": row["decimo_terceiro"],
                "valor_ferias": row["valor_ferias"],
                "dissidio": nome_sindicato  # Aqui entra o nome do sindicato
            })

            folha_total[row["codi_emp"]] += salario

        return {
            "dados": [
                {
                    "codi_emp": codi_emp,
                    "folha_mensal": round(folha_total[codi_emp], 2),
                    "empregados": empregados
                }
                for codi_emp, empregados in agrupado.items()
            ]
        }

    except Exception as e:
        return {"erro": str(e)}
