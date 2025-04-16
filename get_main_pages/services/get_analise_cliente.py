from django.http import JsonResponse
from get_main_pages.services.get_faturamento import get_faturamento
from get_main_pages.services.get_dados_empresa import get_empresa
from get_main_pages.services.get_lanc_e_notas import get_importacoes_empresa
from get_main_pages.services.get_quant_empregados import get_contratados_por_mes
from get_main_pages.services.get_atividades_empresa import get_atividades_empresa_mes

import logging


def get_dados_analise_cliente(data_inicial, data_final):
    try:
        empresas = get_empresa()
        faturamentos = get_faturamento(data_inicial, data_final)
        importacoes = get_importacoes_empresa(data_inicial, data_final)
        contratados = get_contratados_por_mes(data_inicial, data_final)
        atividades = get_atividades_empresa_mes(
            data_inicial, data_final
        )  # <== removido .json()

        # Indexação por código da empresa
        faturamento_dict = {
            str(item["codi_emp"]): item["faturamento"] for item in faturamentos
        }
        importacoes_dict = {
            str(item["codi_emp"]): item["importacoes"] for item in importacoes
        }
        contratados_dict = {
            str(item["codi_emp"]): item["quantidade_ativos"] for item in contratados
        }
        atividades_dict = {str(k): v for k, v in atividades.items()}

        empresas_integradas = []

        for empresa in empresas:
            codigo = str(empresa["codigo_empresa"])

            dados = {
                "codigo_empresa": codigo,
                "nome_empresa": empresa.get("nome_empresa"),
                "cnpj": empresa.get("cnpj"),
                "email": empresa.get("email"),
                "situacao": empresa.get("situacao"),
                "data_cadastro": empresa.get("data_cadastro"),
                "data_inicio_atv": empresa.get("data_inicio"),
                "responsavel": empresa.get("responsavel_legal"),
                "escritorios": empresa.get("escritorios", []),
                "faturamento": faturamento_dict.get(codigo, {}),
                "importacoes": importacoes_dict.get(codigo, {}),
                "empregados": contratados_dict.get(codigo, {}),
                "atividades": atividades_dict.get(codigo, {}),
            }

            empresas_integradas.append(dados)

        return JsonResponse(empresas_integradas, safe=False)

    except Exception as e:
        logging.exception("Erro na integração dos dados do cliente")
        return JsonResponse({"error": str(e)}, status=500)
