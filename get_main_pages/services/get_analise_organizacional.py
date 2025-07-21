from odbc_reader.services import fetch_data

def get_organizacional(start_date=None, end_date=None):
    """
    Versão Final: Busca e consolida dados para todos os cards do dashboard,
    considerando um filtro de data.
    """
    try:
        if start_date is None:
            start_date = '2023-01-01'
        if end_date is None:
            end_date = '2023-12-31'

        query_dissidio = """
            SELECT
                nome,
                mes_base
            FROM bethadba.fosindicatos
        """

        query_valor_por_funcionario = f"""
            SELECT
                emp.nome,
                emp.salario
            FROM 
                bethadba.foempregados AS emp
            LEFT JOIN 
                bethadba.forescisoes AS resc ON emp.codi_emp = resc.codi_emp AND emp.i_empregados = resc.i_empregados
            WHERE 
                emp.admissao <= '{end_date}' 
                AND (resc.demissao IS NULL OR resc.demissao >= '{start_date}')
            ORDER BY 
                emp.salario DESC
        """

        query_valor_por_tipo_calculo = f"""
            SELECT
                CASE lanc.tipo_processo
                    WHEN 11 THEN '11 - Folha Mensal'
                    WHEN 41 THEN '41 - Adiantamento'
                    WHEN 42 THEN '42 - Complementar'
                    WHEN 51 THEN '51 - 13º Adiantamento'
                    WHEN 52 THEN '52 - 13º Integral'
                    WHEN 60 THEN '60 - Férias'  -- Baseado no seu dashboard. A coluna pode ter 61, mas a UI mostra 60.
                    ELSE 'Outros'
                END AS tipo_calculo,
                SUM(lanc.valor_calculado) AS total_valor
            FROM 
                bethadba.FOLANCAMENTOS_EVENTOS AS lanc
            WHERE
                lanc.competencia_inicial BETWEEN '{start_date}' AND '{end_date}'
                AND lanc.valor_calculado IS NOT NULL
            GROUP BY 
                tipo_calculo
            ORDER BY 
                total_valor DESC
        """

        result_dissidio_raw = fetch_data(query_dissidio)
        result_funcionarios_raw = fetch_data(query_valor_por_funcionario)
        result_tipos_calculo_raw = fetch_data(query_valor_por_tipo_calculo)


        meses_map = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        dissidio_final = []
        for item in result_dissidio_raw:
            if item.get('mes_base', 0) > 0:
                dissidio_final.append({"nome_sindicato": item.get('nome'), "mes_base": meses_map.get(item.get('mes_base'), 'Inválido')})
        dissidio_final.sort(key=lambda x: list(meses_map.values()).index(x['mes_base']))

        salarios = [float(func.get('salario', 0)) for func in result_funcionarios_raw]
        total_salarios = sum(salarios)
        funcionarios_final = []
        for func in result_funcionarios_raw:
            salario = float(func.get('salario', 0))
            percentual = (salario / total_salarios) * 100 if total_salarios > 0 else 0
            funcionarios_final.append({"nome": func.get('nome'), "valor": salario, "percentual": round(percentual, 1)})
            
        valores_calculo = [float(calc.get('total_valor', 0)) for calc in result_tipos_calculo_raw]
        total_geral_calculos = sum(valores_calculo)
        calculos_final = []
        for calc in result_tipos_calculo_raw:
            valor = float(calc.get('total_valor', 0))
            percentual = (valor / total_geral_calculos) * 100 if total_geral_calculos > 0 else 0
            calculos_final.append({"nome": calc.get('tipo_calculo'), "valor": valor, "percentual": round(percentual, 1)})

        return {
            "dissidio": dissidio_final,
            "valorPorFuncionario": funcionarios_final,
            "valorPorTipoCalculo": calculos_final
        }

    except Exception as e:
        return {"erro": f"Ocorreu um erro ao processar os dados do dashboard: {str(e)}"}