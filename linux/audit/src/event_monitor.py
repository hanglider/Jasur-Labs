import psutil
import time
from threading import Thread

class EventMonitor:
    def __init__(self, logger):
        self.logger = logger
        self.running = False

    def monitor_processes(self):
        seen_pids = set()
        while self.running:
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                if proc.info['pid'] not in seen_pids:
                    self.logger.log("PROCESS_START", f"User: {proc.info['username']}, Process: {proc.info['name']}")
                    seen_pids.add(proc.info['pid'])
            time.sleep(1)

    def start_monitoring(self):
        self.running = True
        self.thread = Thread(target=self.monitor_processes)
        self.thread.start()

    def stop_monitoring(self):
        self.running = False
        self.thread.join()
