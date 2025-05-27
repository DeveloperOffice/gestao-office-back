from django.http import JsonResponse
from odbc_reader.services import fetch_data
import logging
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

def get_analise_escritorio(start_date, end_date):
    try:
        query_escritorios = """
        SELECT DISTINCT
            geempre.nome_emp AS nome,
            HRCLIENTE.CODI_EMP AS codigo_escritorio,
            HRCLIENTE.I_CLIENTE_FIXO AS codigo_empresa
        FROM bethadba.HRCLIENTE
        INNER JOIN bethadba.geempre ON geempre.codi_emp = HRCLIENTE.CODI_EMP 
        WHERE HRCLIENTE.I_CLIENTE_FIXO IS NOT NULL
        """
        escritorios = fetch_data(query_escritorios)
        
        listaEscritorios = []
        codigos_existentes = set()  # para controle rápido dos códigos já adicionados

        for i in escritorios:
            nome = i["nome"]
            codigo = i['codigo_escritorio']
            if codigo not in codigos_existentes:
                listaEscritorios.append({
                    "nome":nome,
                    "codigo_escritorio": codigo
                    })
                codigos_existentes.add(codigo)

            

    #Feito logica com nome e codigo

    #Iniciar numero de clientes por mês

    query_clientes = """
        SELECT 
"""

        
        
        return listaEscritorios

    except Exception as e:
        logger.error(f"Error in get_analise_escritorio: {str(e)}")
        return {"error": str(e)}