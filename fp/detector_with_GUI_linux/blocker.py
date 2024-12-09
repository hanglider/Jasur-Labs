import subprocess
from config import BLOCKING_ENABLED


def block_ip(ip_address):
    if BLOCKING_ENABLED:
        try:
            subprocess.run(
                ["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"],
                check=True,
            )
            print(f"[!] Blocked IP {ip_address} using iptables")
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to block IP {ip_address}: {e}")
