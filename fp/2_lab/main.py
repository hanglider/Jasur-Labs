import os
import shutil
import time
import json
import logging
from logging.handlers import RotatingFileHandler
import win32serviceutil
import win32service
import win32event
import servicemanager

class BackupDaemon(win32serviceutil.ServiceFramework):
    _svc_name_ = "BackupDaemon"
    _svc_display_name_ = "Backup Daemon"
    _svc_description_ = "A service for regular backup of files."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.load_config("C:\\IT\\Jasur-Labs\\config.json")
        self.setup_logging()

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
            self.source_directory = config['source_directory']
            self.backup_directory = config['backup_directory']
            self.backup_interval = config['backup_interval']
            self.log_file = config['log_file']

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        handler = RotatingFileHandler(self.log_file, maxBytes=1048576, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)

    def backup_files(self):
        timestamp = time.strftime("%Y%m%d%H%M%S")
        backup_path = os.path.join(self.backup_directory, f"backup_{timestamp}")
        try:
            shutil.copytree(self.source_directory, backup_path)
            logging.info(f"Backup created at {backup_path}")
        except Exception as e:
            logging.error(f"Backup failed: {e}")

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        while self.running:
            self.backup_files()
            time.sleep(self.backup_interval)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(BackupDaemon)
