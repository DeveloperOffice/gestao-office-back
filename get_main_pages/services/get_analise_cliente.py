from django.http import JsonResponse
from get_main_pages.services.get_faturamento import get_faturamento
from get_main_pages.services.get_dados_empresa import get_empresa
from get_main_pages.services.get_lanc_e_notas import get_importacoes_empresa
from get_main_pages.services.get_quant_empregados import get_contratados_por_mes

import logging
logger = logging.getLogger(__name__)


def get_dados_analise_cliente(data_inicial, data_final):
    try:
        return get_contratados_por_mes(data_inicial, data_final)

        

    except Exception as e:
        logger.exception("Erro ao processar faturamento com filtro de meses.")
        return {"error": str(e)}
