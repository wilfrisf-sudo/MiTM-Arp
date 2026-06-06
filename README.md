# Laboratorio de Seguridad: Ataque MitM mediante ARP Spoofing

**Autor:** Wilfri Solano Frias  
**Matrícula:** 2024-2364  

---

## 1. Objetivo del Laboratorio
Conocer las vulnerabilidades y peligros reales de la falta de autenticación en los protocolos de resolución de direcciones de Capa 2 (ARP). Se analiza cómo un atacante puede explotar la naturaleza dinámica de los conmutadores e inundar la red con mensajes falsificados para corromper el mapeo de direcciones IP-MAC, permitiendo interceptar o manipular el tráfico de un sistema Windows 10 hacia su Gateway.

---

## 2. Objetivo del Script
Inundar la red local de forma periódica (cada 2 segundos) con respuestas ARP fraudulentas (*Gratuitous/Unicast ARP Replies*). El script asocia dinámicamente la dirección MAC del atacante con la IP del Gateway (ante la víctima) y con la IP de la víctima (ante el Gateway), tomando el control absoluto de los flujos de comunicación.

### 2.1. Requisitos para utilizar la herramienta
* **Sistema Operativo:** Kali Linux.
* **Lenguaje:** Python 3.x.
* **Librerías/Dependencias:** Scapy (módulos básicos del núcleo: `ARP`, `send`, `getmacbyip`).
* **Configuración del Kernel (IP Forwarding):** Obligatorio activar el reenvío de paquetes en la terminal de Kali antes de ejecutar la herramienta:  
  `sudo sysctl -w net.ipv4.ip_forward=1`  
  *(Si se omite este paso, el ataque bloqueará el tráfico de internet en Windows 10, convirtiéndose en un ataque DoS).*
* **Entorno de Red:** Los tres nodos deben coexistir en el mismo dominio de difusión (VLAN 1) y el switch de acceso debe permitir la transmisión libre de tramas ARP. El script requiere privilegios de administrador (`sudo`).

### 2.2. Parámetros Usados
El script admite y manipula las siguientes variables y funciones específicas:

**Función de Suplantación `spoof` (Líneas 7 y 12)**
* `getmacbyip`: Envía un *ARP Request* automático para capturar la dirección MAC legítima de los objetivos de forma dinámica en la red.
* `op=2`: Fuerza el formato del paquete para que actúe estrictamente como un *ARP Reply* (respuesta).
* `psrc`: Dirección IP que se desea suplantar ante el objetivo (`IP_GATEWAY` o `IP_VICTIMA`).

**Bloque Principal y Temporizador (Líneas 24, 25 y 37)**
* `IP_VICTIMA = "192.168.124.133"` y `IP_GATEWAY = "192.168.124.1"`: Asignación estricta de las direcciones IP correspondientes al entorno real de pruebas.
* `time.sleep(2)`: Intervalo cíclico de re-envenenamiento configurado para ganarle a las actualizaciones automáticas legítimas de las tablas de los sistemas operativos.

---

## 3. Documentación del Funcionamiento del Script
El switch SWI2 conmuta las tramas basándose en las direcciones de hardware (MAC). Al ejecutarse el script en un bucle infinito, la máquina de la víctima Windows 10 recibe de forma continua un paquete ARP que le indica falsamente que la IP del Router (`.1`) corresponde a la dirección MAC de Kali. Al mismo tiempo, el Router Cisco recibe un paquete indicando que la IP del Windows 10 (`.133`) se ubica en la MAC de Kali.

El switch registra estos movimientos dinámicos en su plano de datos. Cuando Windows 10 intenta enviar información hacia redes externas, el conmutador redirige los paquetes hacia el puerto `Ethernet0/1` (Atacante) en lugar del puerto `Ethernet0/0` (Gateway). Gracias a la activación previa de `ip_forward=1`, el sistema Kali Linux procesa la información interceptada y la reenvía al enrutador original, completando la intercepción silenciosa (*Man-in-the-Middle*).

---

## 4. Documentación de la Red

### 4.1. Topología
* **Descripción:** Infraestructura virtualizada en GNS3 para evaluar el envenenamiento de tablas de transposición IP-MAC y la desviación del tráfico mediante inyección de control en accesos.
* **VLANs Configuradas:** VLAN 1 (Nativa / Por defecto).
* **Direccionamiento IP:**
  * **Segmento de Red:** `192.168.124.0` / `255.255.255.0`
  * **Router Cisco (Gateway de la red):** IP `192.168.124.1` configurada en su interfaz `Ethernet0/0`.
  * **Estación Atacante (Kali Linux):** IP estática `192.168.124.135` (Interfaz `eth0`).
  * **Víctima (Windows 10):** IP estática `192.168.124.133` asignada en su adaptador de red.
* **Interfaces Clave (SWI2 - Cisco IOU Layer 2):**
  * `Ethernet0/0`: Conectado directamente al Router (Gateway).
  * `Ethernet0/1`: Conectado a la máquina atacante Kali Linux.
  * `Ethernet0/2`: Conectado a la víctima Windows 10.

---

## 5. Contramedidas (Mitigación)

### 5.1 El Estándar de la Industria: Dynamic ARP Inspection (DAI)
En redes empresariales, el método definitivo para bloquear este ataque desde el switch es *Dynamic ARP Inspection* (DAI), un protocolo de seguridad que intercepta y valida todas las solicitudes y respuestas ARP entrantes contra una base de datos segura y confiable (creada por *DHCP Snooping*). 

> **Nota Técnica de Laboratorio:** Durante las prácticas en GNS3 se determinó que la imagen virtual de Capa 2 utilizada (`i86bi-linux-l2-ipbasek9`) carece del software necesario para ejecutar esta función, emitiendo un error de comando inválido (*Invalid input detected*) que confirmó la incompatibilidad de la simulación con DAI y obligó a aplicar la mitigación de forma estática en los extremos.

### 5.2 Mitigación Estática en los Extremos (Hosts)
Ante la imposibilidad de delegar la seguridad en la infraestructura del switch central, la vulnerabilidad se mitigó de forma definitiva obligando a los extremos de la topología (Windows 10 y Router Cisco) a congelar sus asignaciones de Capa 2 de manera manual, transformando sus tablas ARP dinámicas en registros permanentes e inmunes al script:

**A. Configuración Estática en la Víctima (Windows 10):**
Se abre una terminal de CMD con privilegios de Administrador y se ejecuta un amarre permanente de la IP y MAC del Gateway para obligar al sistema operativo a ignorar las respuestas ARP falsas del atacante:

netsh interface ipv4 add neighbors "Ethernet" "192.168.124.1" "aa-bb-cc-00-01-00"

B. Configuración Estática en el Gateway (Router Cisco):
Para evitar que el script de automatización siguiera engañando al enrutador con respecto a la ubicación de la víctima, se ingresó a la configuración global del Router y se fijó la identidad física real del host Windows 10:

Router# configure terminal
Router(config)# arp 192.168.124.133 000c.294f.b6be arpa

6. Evidencias

6.1. Demostración en Video
En el siguiente enlace se encuentra el video demostrativo donde se visualiza la topología con la ejecución del ataque y la aplicación de la contramedida:

https://www.youtube.com/watch?v=vMMKubAXT8Y&list=PLGfNWxn7Di3BhsEEifmTJKXP4_U9fla7P&index=6

6.2. Capturas de Pantalla

A. Diseño de la Topología en GNS3 

<img width="587" height="433" alt="imagen" src="https://github.com/user-attachments/assets/783fedf4-396e-44c1-a041-98414aaebb0e" />

B. captura del arp dinamico en consola windows 10

<img width="493" height="177" alt="imagen" src="https://github.com/user-attachments/assets/18d27430-3475-44d7-ad3f-5e69039589f3" />

C. Ejecución del Script en Kali Linux 

<img width="829" height="205" alt="imagen" src="https://github.com/user-attachments/assets/c4124d5f-5cd1-4749-92e1-1813e9713f68" />

D. Impacto del Ataque (Consola de Windows 10)

<img width="514" height="192" alt="imagen" src="https://github.com/user-attachments/assets/54d7a4c4-3596-4ca9-a96e-498a968b70c9" />

E. Aplicación de Contramedidas (DHCP Snooping Activo) 

<img width="505" height="100" alt="imagen" src="https://github.com/user-attachments/assets/13a1e9f7-e68d-4855-8b8f-13d27fd39941" />

<img width="847" height="36" alt="imagen" src="https://github.com/user-attachments/assets/1a53dce1-22c6-447e-ae59-e405c2c17d94" />

<img width="483" height="182" alt="imagen" src="https://github.com/user-attachments/assets/39f578d5-d860-40e1-8201-ab3e95cba079" />
