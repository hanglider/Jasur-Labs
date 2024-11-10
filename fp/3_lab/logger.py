import logging

logging.basicConfig(filename="suspicious_traffic.log", level=logging.INFO)

def log_suspicious_event(ip, reason):
    logging.info(f"Suspicious IP: {ip}, Reason: {reason}")
    print(f"Logged suspicious activity for IP {ip}: {reason}")