from scapy.all import sniff, IP, TCP, UDP, DNS, DNSQR
from datetime import datetime
import socket

# ===== CONFIGURAÇÃO =====
REDE_LOCAL = "192.168.18."
IGNORAR_MULTICAST = ("224.", "239.")
# =======================

dns_cache = {}      # IP -> dominio
ptr_cache = {}      # IP -> hostname PTR


def resolver_ptr(ip):
    if ip in ptr_cache:
        return ptr_cache[ip]
    try:
        nome = socket.gethostbyaddr(ip)[0]
    except:
        nome = None
    ptr_cache[ip] = nome
    return nome


def processar_pacote(pkt):
    # 1) CAPTURA DNS (aprende nomes reais)
    if pkt.haslayer(DNS) and pkt.haslayer(DNSQR):
        if pkt[DNS].qr == 0:  # query
            dominio = pkt[DNSQR].qname.decode(errors="ignore").rstrip(".")
            if pkt.haslayer(IP):
                ip_origem = pkt[IP].src
                dns_cache[ip_origem] = dominio
        return

    # 2) PACOTES IP
    if not pkt.haslayer(IP):
        return

    src = pkt[IP].src
    dst = pkt[IP].dst

    # Ignorar multicast
    if src.startswith(IGNORAR_MULTICAST) or dst.startswith(IGNORAR_MULTICAST):
        return

    # Direção
    if src.startswith(REDE_LOCAL):
        direcao = "SAIDA"
        ip_externo = dst
    elif dst.startswith(REDE_LOCAL):
        direcao = "ENTRADA"
        ip_externo = src
    else:
        direcao = "EXTERNO"
        ip_externo = dst

    # Protocolo
    if pkt.haslayer(TCP):
        proto = "TCP"
    elif pkt.haslayer(UDP):
        proto = "UDP"
    else:
        proto = "OUTRO"

    # Resolver nome
    nome = dns_cache.get(ip_externo)
    if not nome:
        nome = resolver_ptr(ip_externo)

    if not nome:
        nome = "DESCONHECIDO"

    print(
        f"[{datetime.now().strftime('%H:%M:%S')}] "
        f"{direcao} | {src} -> {dst} | {proto} | {len(pkt)} bytes | {nome}"
    )


print("Monitoramento iniciado (DNS + Tráfego IP)...")
sniff(prn=processar_pacote, store=False)
