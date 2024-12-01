from scapy.all import IP, TCP, send

def test_port_scan():
    target_ip = "127.0.0.1"
    ports_to_scan = range(1, 101)  # Сканирование первых 100 портов
    for port in ports_to_scan:
        packet = IP(dst=target_ip) / TCP(dport=port)
        send(packet, verbose=0)

if __name__ == "__main__":
    test_port_scan()