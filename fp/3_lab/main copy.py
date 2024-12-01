from scapy.all import sniff
from detector import detect_suspicious

def start_monitoring():
    sniff(prn=detect_suspicious, store=0)

if __name__ == "__main__":
    start_monitoring()