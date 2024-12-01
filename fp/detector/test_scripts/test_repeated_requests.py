from scapy.all import IP, TCP, send

def test_repeated_requests():
    for _ in range(10):  # Число запросов выше порогового значения
        packet = IP(dst="127.0.0.1") / TCP(dport=80)
        send(packet, verbose=0)

if __name__ == "__main__":
    test_repeated_requests()