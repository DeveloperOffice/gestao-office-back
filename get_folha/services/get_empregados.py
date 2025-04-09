from django.http import JsonResponse
from odbc_reader.services import fetch_data


def get_lista_empregados():
    try:
        query = """SELECT
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
                    foempregados.estado_civil,
                    foempregados.nacionalidade,
                    foempregados.identidade,
                    foempregados.cpf,
                    foempregados.i_cargos,
                    foempregados.grau_instrucao,
                    foempregados.emprego_ant,
                    foempregados.ini_praz_det,
                    foempregados.fim_praz_det,
                    foempregados.DATA_PROJETADA_TERMINO_AVISO_PREVIO_INDENIZADO,
                    foempregados.DATA_REAL_DN_AFASTAMENTO_DA,
                    foempregados.DATA_DESLIGAMETO_REINTEGRACAO

                    FROM bethadba.foempregados"""
        result = fetch_data(query)
        
    except Exception as e:
        
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse(result, safe=False)

