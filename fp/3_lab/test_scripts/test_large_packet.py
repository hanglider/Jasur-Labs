from scapy.all import IP, UDP, send

def test_large_packet():
    large_packet = IP(dst="127.0.0.1") / UDP(dport=80) / ("X" * 2000)  # Пакет размером 2000 байт
    send(large_packet, verbose=0)

if __name__ == "__main__":
    test_large_packet()