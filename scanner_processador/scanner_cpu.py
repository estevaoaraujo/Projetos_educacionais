import psutil
import time

print("Mapeando processos (Windows)...\n")

# Inicialização do cálculo de CPU
for p in psutil.process_iter():
    try:
        p.cpu_percent(interval=None)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

time.sleep(1)

while True:
    print("-" * 90)
    print(f"{'PID':<8}{'Processo':<25}{'CPU%':<8}{'Afinidade (núcleos permitidos)'}")
    print("-" * 90)

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.pid
            nome = (proc.name() or "")[:24]
            cpu = proc.cpu_percent(interval=None)
            afinidade = proc.cpu_affinity()

            print(f"{pid:<8}{nome:<25}{cpu:<8.1f}{afinidade}")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(2)
