from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def sucess(request):
    return JsonResponse({'conection': 'success'}, status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', sucess),
    path('empresa/', include('empresas.urls'))
]
