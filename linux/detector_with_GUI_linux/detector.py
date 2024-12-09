from scapy.all import IP, TCP
from config import MAX_PACKET_SIZE, PORT_SCAN_THRESHOLD, REPEAT_REQUEST_THRESHOLD
from logger import log_suspicious_event

suspicious_ips = {}


def detect_suspicious(packet, gui=None):
    if IP in packet:
        ip_src = packet[IP].src

        # Проверка на аномально большие пакеты
        if len(packet) > MAX_PACKET_SIZE:
            if gui:
                gui.add_request(ip_src, "Large packet size")
            log_suspicious_event(ip_src, "Large packet size")
            return

        # Проверка на сканирование портов
        if TCP in packet:
            if ip_src not in suspicious_ips:
                suspicious_ips[ip_src] = []
            suspicious_ips[ip_src].append(packet[TCP].dport)

            if len(set(suspicious_ips[ip_src])) > PORT_SCAN_THRESHOLD:
                if gui:
                    gui.add_request(ip_src, "Port scanning")
                log_suspicious_event(ip_src, "Port scanning")
                return

        # Проверка на повторяющиеся запросы
        if len(suspicious_ips.get(ip_src, [])) > REPEAT_REQUEST_THRESHOLD:
            if gui:
                gui.add_request(ip_src, "Frequent repeated requests")
            log_suspicious_event(ip_src, "Frequent repeated requests")
            return

        # Если все нормально
        if gui:
            gui.add_request(ip_src)
