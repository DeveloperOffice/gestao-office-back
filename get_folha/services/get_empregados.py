from collections import defaultdict
from django.http import JsonResponse
from odbc_reader.services import fetch_data


def get_lista_empregados():
    try:
        query = """
            SELECT
                foempregados.codi_emp,
                foempregados.i_empregados,
                foempregados.i_filiais,
                foempregados.nome,
                foempregados.horas_mes,
                foempregados.horas_semana,
                foempregados.horas_dia,
                foempregados.admissao,
                foempregados.salario,
                foempregados.data_nascimento,
                foempregados.venc_ferias,
                foempregados.sexo,
                foempregados.uf_nascimento,

                CASE foempregados.estado_civil
                    WHEN 'C' THEN 'Casado'
                    WHEN 'D' THEN 'Divorciado'
                    WHEN 'J' THEN 'Separado judicialmente'
                    WHEN 'O' THEN 'Concubinado'
                    WHEN 'S' THEN 'Solteiro'
                    WHEN 'U' THEN 'União estável'
                    WHEN 'V' THEN 'Viuvo'
                    ELSE 'Não informado'
                END AS estado_civil,

                CASE foempregados.nacionalidade
                    WHEN 10 THEN 'Brasileiro'
                    WHEN 11 THEN 'Naturalizado'
                    WHEN 12 THEN 'Argentino'
                    WHEN 13 THEN 'Boliviano'
                    WHEN 14 THEN 'Chileno'
                    WHEN 15 THEN 'Paraguaio'
                    WHEN 16 THEN 'Uruguaio'
                    WHEN 17 THEN 'Alemao'
                    WHEN 18 THEN 'Belga'
                    WHEN 19 THEN 'Britanico'
                    WHEN 20 THEN 'Canadense'
                    WHEN 21 THEN 'Espanhol'
                    WHEN 22 THEN 'Norte-Americano'
                    WHEN 23 THEN 'Frances'
                    WHEN 24 THEN 'Suico'
                    WHEN 25 THEN 'Italiano'
                    WHEN 26 THEN 'Japones'
                    WHEN 27 THEN 'Chines'
                    WHEN 28 THEN 'Coreano'
                    WHEN 29 THEN 'Portugues'
                    WHEN 30 THEN 'Outros latino-am.'
                    WHEN 31 THEN 'Outros asiaticos'
                    WHEN 32 THEN 'Outros'
                    ELSE 'Não informado'
                END AS nacionalidade,

                foempregados.identidade,
                foempregados.cpf,
                foempregados.i_cargos,
                focargos.nome AS nome_cargo,

                CASE foempregados.grau_instrucao
                    WHEN 1 THEN 'Analfabeto'
                    WHEN 2 THEN 'Primario incompleto'
                    WHEN 3 THEN 'Primario completo'
                    WHEN 4 THEN 'Ginasio incompleto'
                    WHEN 5 THEN 'Ginasio completo'
                    WHEN 6 THEN '2o. grau incompleto'
                    WHEN 7 THEN '2o. grau completo'
                    WHEN 8 THEN 'Superior incompleto'
                    WHEN 9 THEN 'Superior completo'
                    WHEN 10 THEN 'Mestrado'
                    WHEN 11 THEN 'Doutorado'
                    WHEN 12 THEN 'Ph. D.'
                    WHEN 13 THEN 'Pós Graduação'
                    ELSE 'Não informado'
                END AS grau_instrucao,

                foempregados.emprego_ant,
                forescisoes.demissao,

                CASE forescisoes.motivo
                    WHEN 1 THEN 'Demitido com Justa Causa'
                    WHEN 2 THEN 'Demitido sem Justa Causa'
                    WHEN 3 THEN 'Recisão indireta'
                    WHEN 4 THEN 'Pedido de demissão sem Justa Causa'
                    WHEN 5 THEN 'Cessão do empregado'
                    WHEN 6 THEN 'Transferência do empregado sem ônus para outra empresa'
                    WHEN 8 THEN 'Morte'
                    WHEN 10 THEN 'Recisão contrato experiência antecipado pelo empregador'
                    WHEN 11 THEN 'Recisão contrato experiência antecipado pelo empregado'
                    WHEN 12 THEN 'Término contrato de experiência'
                    WHEN 13 THEN 'Morte por acidente de trabalho'
                    WHEN 14 THEN 'Morte por doença profissional'
                    WHEN 22 THEN 'Término de contrato de trabalho por tempo determinado'
                    WHEN 23 THEN 'Antecipado pelo empregador (tempo determinado)'
                    WHEN 24 THEN 'Antecipado pelo empregado (tempo determinado)'
                    WHEN 27 THEN 'Transferência do empregado sem ônus para outra empresa'
                    WHEN 28 THEN 'Culpa recíproca'
                    WHEN 29 THEN 'Extinção da empresa'
                    WHEN 30 THEN 'Extinção da empresa por força maior'
                    WHEN 40 THEN 'Morte por acidente de trabalho de trajeto'
                    WHEN 41 THEN 'Falecimento do empregador individual s/ continuação da atividade'
                    WHEN 42 THEN 'Falecimento do empregador individual por opção do empregado'
                    WHEN 44 THEN 'Rescisão por acordo entre as partes'
                    WHEN 46 THEN 'Rescisão por motivo de força maior'
                    WHEN 47 THEN 'Mudança de CPF'
                    ELSE null
                END AS motivo_demissao

            FROM bethadba.foempregados

            -- JOIN para trazer nome do cargo
            LEFT JOIN bethadba.focargos
                ON foempregados.codi_emp = focargos.codi_emp
                AND foempregados.i_cargos = focargos.i_cargos

            -- JOIN para trazer dados da demissão
            LEFT JOIN bethadba.forescisoes
                ON foempregados.codi_emp = forescisoes.codi_emp
                AND foempregados.i_empregados = forescisoes.i_empregados
        """
        result = fetch_data(query)
        
        empresas_dict = defaultdict(list)
        for row in result:
            codi_emp = row.get("codi_emp")
            if codi_emp is not None:
                row = dict(row)  # Garante que row é mutável
                row.pop("codi_emp", None)  # Remove codi_emp de dentro do funcionário
                empresas_dict[codi_emp].append(row)

        # Transformar em lista de objetos com a estrutura desejada
        dados_formatados = []
        for codi_emp, empregados in empresas_dict.items():
            dados_formatados.append({
                "codi_emp": codi_emp,
                "empregados": empregados
            })

        return JsonResponse(dados_formatados, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
