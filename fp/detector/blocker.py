from scapy.all import IP, ICMP, send
from config import BLOCKING_ENABLED

def block_ip(ip_address):
    if BLOCKING_ENABLED:
        packet = IP(dst=ip_address) / ICMP(type=3, code=1)
        send(packet, verbose=0)
        print(f"[!] Blocked IP {ip_address}")