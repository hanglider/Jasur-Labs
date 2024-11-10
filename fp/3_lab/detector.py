from scapy.all import IP, TCP
from config import MAX_PACKET_SIZE, PORT_SCAN_THRESHOLD, REPEAT_REQUEST_THRESHOLD
from blocker import block_ip
from logger import log_suspicious_event

suspicious_ips = {}

def detect_suspicious(packet):
    if IP in packet:
        ip_src = packet[IP].src
        # Проверка на аномально большие пакеты
        if len(packet) > MAX_PACKET_SIZE:
            log_suspicious_event(ip_src, "Large packet size")
            block_ip(ip_src)
        
        # Проверка на сканирование портов
        if TCP in packet:
            if ip_src not in suspicious_ips:
                suspicious_ips[ip_src] = []
            suspicious_ips[ip_src].append(packet[TCP].dport)
            
            if len(set(suspicious_ips[ip_src])) > PORT_SCAN_THRESHOLD:
                log_suspicious_event(ip_src, "Port scanning")
                block_ip(ip_src)
        
        # Проверка на повторяющиеся запросы (пример)
        if len(suspicious_ips.get(ip_src, [])) > REPEAT_REQUEST_THRESHOLD:
            log_suspicious_event(ip_src, "Frequent repeated requests")
            block_ip(ip_src)