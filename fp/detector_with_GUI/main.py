from scapy.all import sniff
from threading import Thread
from GUI import TrafficMonitor
from detector import detect_suspicious

def start_sniffing(gui):
    sniff(prn=lambda packet: detect_suspicious(packet, gui), store=0)

if __name__ == "__main__":
    gui = TrafficMonitor()

    # Запуск сниффера в отдельном потоке
    sniffer_thread = Thread(target=start_sniffing, args=(gui,), daemon=True)
    sniffer_thread.start()

    # Запуск GUI
    gui.mainloop()
