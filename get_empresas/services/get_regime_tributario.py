from django.http import JsonResponse
from odbc_reader.services import fetch_data

def get_regime():
    try:        
        query = """SELECT
                EFPARAMETRO_VIGENCIA.CODI_EMP,
                EFPARAMETRO_VIGENCIA.VIGENCIA_PAR,
                EFPARAMETRO_VIGENCIA.RFED_PAR,
                SIMPLESN_OPTANTE_PAR

                FROM bethadba.EFPARAMETRO_VIGENCIA"""
                
        result = fetch_data(query)

  
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)
    
    return result

def get_regime_secundario(lista_id):
    try:        
        query = f"""SELECT
                foparmto.codi_emp,
                foparmto.CLASSIFICACAO_TRIBUTARIA,
                foparmto.COOPERATIVA,
                foparmto.CONSTRUTORA,
                foparmto.PRODUTOR_RURAL,
                foparmto.GERAR_ESOCIAL_DOMESTICO
                FROM bethadba.foparmto
                WHERE foparmto.codi_emp IN ({','.join(map(str, lista_id))}) """
                
        result = fetch_data(query)

  
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)
    
    return result
