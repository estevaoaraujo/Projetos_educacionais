from scapy.all import sniff, IP, TCP, UDP
from datetime import datetime

def analisar_pacote(pkt):
    if IP in pkt:
        ip = pkt[IP]
        protocolo = "OUTRO"

        if TCP in pkt:
            protocolo = "TCP"
        elif UDP in pkt:
            protocolo = "UDP"

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"{ip.src} -> {ip.dst} | "
            f"PROTO: {protocolo} | "
            f"SIZE: {len(pkt)} bytes"
        )

print("Iniciando captura de pacotes...")
sniff(prn=analisar_pacote, store=False)
