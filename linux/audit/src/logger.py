import datetime

class Logger:
    def __init__(self, log_file):
        self.log_file = log_file

    def log(self, event_type, message):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"{timestamp} | {event_type} | {message}\n"
        with open(self.log_file, "a") as file:
            file.write(log_entry)
