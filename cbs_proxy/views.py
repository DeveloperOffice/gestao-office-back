import subprocess, threading, time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def _start_calc_background():
    # Inicia a calculadora no WSL e injeta "1" + Enter (duas vezes, por segurança)
    command = ["wsl", "-d", "calculadora", "--cd", "/calculadora", "--exec", "bash", "start.sh"]
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        # envia a opção 1 e dois Enters
        if proc.stdin:
            proc.stdin.write("1")
            proc.stdin.flush()
        # dá um pequeno tempo pra subir o servidor local (porta 80)
        time.sleep(2)
    except Exception:
        pass
    # não chamamos communicate(); deixamos rodar em background

@csrf_exempt
@require_http_methods(["POST"])  # só POST pra “start”
def calcular(request):
    # Dispara em thread separada para nunca bloquear a resposta HTTP
    t = threading.Thread(target=_start_calc_background, daemon=True)
    t.start()
    return JsonResponse({"ok": True, "message": "Calculadora iniciada em background. Abra http://localhost/."})