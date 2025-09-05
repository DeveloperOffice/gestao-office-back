import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def run_calculadora():
    try:
        command = ["wsl", "-d", "calculadora", "--cd", "/calculadora", "--exec", "bash", "start.sh"]
        # Tenta: opção 1 + um Enter extra (caso a calculadora peça "pressione Enter para continuar")
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate("1")

        if proc.returncode != 0:
            return None, f"Erro ao executar o script (code {proc.returncode}): {stderr.strip()} - Saída: {stdout[:500]}"

        return stdout, None

    except subprocess.TimeoutExpired as e:
        # Mata o processo se estourar o tempo
        try:
            proc.kill()
        except Exception:
            pass
        return None, f"Tempo limite excedido ao executar a calculadora ({e.timeout}s)."
    except FileNotFoundError:
        return None, "WSL não encontrado. Verifique se o WSL está instalado e acessível pelo serviço do Django."
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}"

@csrf_exempt
@require_http_methods(["GET", "POST"])
def calcular(request):
    output, error = run_calculadora()
    if error:
        return JsonResponse({"error": error}, status=500)
    return JsonResponse({"resultado": output})
