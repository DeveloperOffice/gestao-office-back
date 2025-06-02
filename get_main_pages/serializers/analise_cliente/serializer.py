# get_main_pages/serializers/cliente.py
from rest_framework import serializers

class AnaliseClienteRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(
        help_text="Data de início no formato YYYY-MM-DD"
    )
    end_date = serializers.DateField(
        help_text="Data de fim no formato YYYY-MM-DD"
    )
    api_token = serializers.CharField(
        help_text="API token gerada pela própria API"
    )

class EscritorioSerializer(serializers.Serializer):
    escritorio = serializers.IntegerField(
        help_text="ID do escritório"
    )
    id_cliente = serializers.IntegerField(
        help_text="ID do cliente no sistema"
    )
    valor_contrato = serializers.FloatField(
        help_text="Valor do contrato (pode ser null)",
        allow_null=True
    )

class ImportacoesSerializer(serializers.Serializer):
    entradas = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Contagem de entradas por mês"
    )
    saidas = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Contagem de saídas por mês"
    )
    servicos = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Contagem de serviços por mês"
    )
    lancamentos = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Contagem de lançamentos por mês"
    )
    lancamentos_manuais = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Contagem de lançamentos manuais por mês"
    )
    total_entradas = serializers.IntegerField(
        help_text="Total de entradas"
    )
    total_saidas = serializers.IntegerField(
        help_text="Total de saídas"
    )
    total_servicos = serializers.IntegerField(
        help_text="Total de serviços"
    )
    total_lancamentos = serializers.IntegerField(
        help_text="Total de lançamentos"
    )
    total_lancamentos_manuais = serializers.IntegerField(
        help_text="Total de lançamentos manuais"
    )
    total_geral = serializers.IntegerField(
        help_text="Total geral de importações"
    )

class AnaliseClienteResponseSerializer(serializers.Serializer):
    codigo_empresa = serializers.CharField(
        help_text="Código interno da empresa"
    )
    nome_empresa = serializers.CharField(
        help_text="Razão social completa"
    )
    cnpj = serializers.CharField(
        help_text="CNPJ no formato somente números"
    )
    email = serializers.EmailField(
        help_text="E-mail cadastrado (pode ser null)",
        allow_null=True
    )
    situacao = serializers.CharField(
        help_text="Situação cadastral"
    )
    data_cadastro = serializers.DateField(
        help_text="Data de cadastro no sistema"
    )
    data_inicio_atv = serializers.DateField(
        help_text="Data de início de atividades"
    )
    responsavel = serializers.CharField(
        help_text="Responsável legal (pode ser null)",
        allow_null=True
    )
    escritorios = EscritorioSerializer(
        many=True,
        help_text="Lista de escritórios vinculados"
    )
    faturamento = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        help_text="Faturamento mensal e percentual de variação"
    )
    importacoes = ImportacoesSerializer(
        help_text="Detalhes de importações e totais"
    )
    empregados = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Número de empregados ativos por mês"
    )
    atividades = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Contagem de atividades por mês (e total)"
    )
