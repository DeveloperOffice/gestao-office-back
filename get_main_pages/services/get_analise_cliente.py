from django.http import JsonResponse
from get_main_pages.services.get_faturamento import get_faturamento
from get_main_pages.services.get_dados_empresa import get_empresa
import logging
logger = logging.getLogger(__name__)


def get_dados_analise_cliente(data_inicial, data_final):
    try:
        result = get_empresa()

        return result

    except Exception as e:
        logger.exception("Erro ao processar faturamento com filtro de meses.")
        return JsonResponse({"error": str(e)}, status=500)
