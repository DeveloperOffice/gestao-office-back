from django.http import JsonResponse
from get_main_pages.services.get_faturamento import get_faturamento
import logging
logger = logging.getLogger(__name__)


def get_dados_analise_cliente(data_inicial, data_final):
    try:
        result = get_faturamento(data_inicial, data_final)

        return result

    except Exception as e:
        logger.exception("Erro ao processar faturamento com filtro de meses.")
        return JsonResponse({"error": str(e)}, status=500)
