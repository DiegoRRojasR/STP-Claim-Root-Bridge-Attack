# STP-Claim-Root-Bridge-Attack

## Video (máx. 8 minutos)
[![Ver video en YouTube](https://img.youtube.com/vi/a57EDA6q1Ys/0.jpg)](https://youtu.be/a57EDA6q1Ys)

---

# Informe Técnico: Spanning-tree Protocol Claim Root Bridge Attack (STP Attack)

## 1-) Objetivo y Mecánica del Script.
La finalidad principal de esta práctica es gestionar la topología lógica de una red conmutada a través del ataque al protocolo **Spanning Tree Protocol (STP)**. El script, creado en Python con la librería **Scapy**, permite de manera automatizada la creación e inyección de tramas **BPDU** (Unidades de datos del protocolo de puente) maliciosas "superiores". Su funcionamiento se basa en solicitar la identidad del Root Bridge estableciendo una prioridad de puente de **0** (la más alta que puede ser). Cuando la red se inunda con estos paquetes, los switches legítimos vuelven a calcular su topología, de forma que el nodo central del árbol de expansión pasa a ser la máquina del atacante. Esto hace posible que se intercepten tramas que por lo general no transitan por este host, posibilitando ataques **Man-in-the-Middle (MitM)** o de **denegación de servicio (DoS)**.

<img width="728" height="579" alt="Screenshot 2026-02-11 020502" src="https://github.com/user-attachments/assets/431b1188-bac0-4895-8aed-fee82d310a4b" />

---

## 2-) Escenario de Laboratorio y Topología.
En un ambiente simulado de **PNETLab**, la prueba de concepto se implementa para simular la infraestructura de una red. La topología está compuesta por dos switches multicapa de Cisco que están conectados entre sí, creando así bucles físicos. El direccionamiento IP es administrado en la subred **10.24.9.0/24**, y el atacante vive en la interfaz **eth0** de una instancia de **Kali Linux** con dirección IP **10.24.9.18**. El switch con la dirección MAC más baja o la prioridad establecida manualmente actúa como **Root Bridge** en circunstancias normales. Sin embargo, cuando comienza el ataque, la topología se orienta hacia el atacante, obligando a las interfaces de los switches reales a entrar en estados de **Blocking** o **Forwarding** según la nueva jerarquía maliciosa.

<img width="829" height="879" alt="Screenshot 2026-02-10 213221" src="https://github.com/user-attachments/assets/d5dffcdc-4346-43a2-bba4-da854dbfe850" />

---

## 3-) Parámetros de Operación y Requisitos.
Para llevar a cabo el script **stp_attack.py** de manera eficaz, es crucial tener privilegios de **root**, debido a que para crear tramas Ethernet personalizadas de Capa 2 se necesita acceso directo a los sockets de red. En este ataque, los parámetros operativos establecidos comprenden:

- **Número de paquetes (-n)**
- **Prioridad del puente malicioso (-p)**
- **Intervalo entre transmisiones (-t)**
- **Interfaz de red (-i)**

<img width="378" height="25" alt="Screenshot 2026-02-11 021016" src="https://github.com/user-attachments/assets/3b22f40d-a89c-4b00-b7c6-8d0b4f0c8daf" />

En esta situación, se empleó un intervalo de **2 segundos** para que coincidiera con el **Hello Time** por defecto de STP y así garantizar que los interruptores mantuvieran la información del atacante como vigente y no retrocedieran a la topología inicial debido al timeout.

---

## 4-) Análisis de Resultados y Capturas.
Durante la fase de validación, se observó en la consola del atacante el envío continuo de BPDUs reclamando el liderazgo de la red.

<img width="474" height="326" alt="Screenshot 2026-02-11 021232" src="https://github.com/user-attachments/assets/28b52711-27a7-4190-8709-2e6f8f2eeed1" />

Al verificar el estado del protocolo en los switches mediante el comando `show spanning-tree`, se confirmó que el Root Bridge original fue desplazado.

<img width="819" height="482" alt="Screenshot 2026-02-11 021409" src="https://github.com/user-attachments/assets/b71f8dc9-d51e-4248-ab19-87fba213df7b" />

Las capturas de tráfico en Wireshark revelaron que las tramas enviadas por el script utilizan la dirección MAC de destino multicast **01:80:c2:00:00:00** (Wireshark lo traduce automaticamente a **"Spanning-tree-(for-bridges)_00"**), característica de STP.

<img width="1001" height="377" alt="Screenshot 2026-02-11 021725" src="https://github.com/user-attachments/assets/0a003722-5b92-4ea3-9ae3-17cdbb8cdb51" />

El impacto inmediato fue una breve interrupción en la conectividad mientras la red convergía, seguida por la reorientación del tráfico hacia el puerto del atacante, demostrando la vulnerabilidad de la red ante la falta de autenticación en las tramas de control.

---

## V-) Medidas de Mitigación y Protección.
Se recomienda encarecidamente la aplicación de medidas de seguridad de Capa 2 en cada uno de los puertos de acceso de los conmutadores ya que es la solución propuesta para contrarrestar este vector de ataque. **BPDU Guard** es el sistema de protección más eficaz, ya que desactiva de manera automática cualquier puerto que reciba un paquete BPDU, suponiendo que un puerto de usuario no debería transmitir ese tipo de tráfico. Además, es necesario establecer **Root Guard** en los puertos que se conectan a switches autorizados para prevenir que un puente externo asuma el papel de raíz. Por último, la asignación manual de prioridades de puente (asignando valores altos para la distribución y bajos para los núcleos) permite que sea más difícil que un atacante obtenga por accidente o deliberadamente una prioridad superior.

