from django.shortcuts import render
from django.http import JsonResponse
from odbc_reader.services import fetch_data

def get_empresas(request):
    query = 'SELECT * FROM bethadba.geempre'
    result = fetch_data(query)
    return JsonResponse({"Empresas": result}, safe=False)