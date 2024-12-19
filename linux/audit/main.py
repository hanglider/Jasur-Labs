import os
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import matplotlib.pyplot as plt
import threading


class EventLogger(FileSystemEventHandler):
    """Класс для обработки событий файловой системы."""

    def __init__(self, log_file):
        self.log_file = log_file

    def log_event(self, event_type, src_path):
        event = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event_type,
            "file_path": src_path,
            "user": os.getlogin()
        }
        with open(self.log_file, "a") as log:
            log.write(json.dumps(event) + "\n")

    def on_modified(self, event):
        if not event.is_directory:
            self.log_event("MODIFIED", event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.log_event("CREATED", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.log_event("DELETED", event.src_path)


class EventMonitor:
    """Класс для запуска наблюдателя."""

    def __init__(self, path, log_file):
        self.path = path
        self.log_file = log_file
        self.event_handler = EventLogger(log_file)
        self.observer = Observer()

    def start(self):
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        print(f"Monitoring started on {self.path}. Logs saved to {self.log_file}.")

    def stop(self):
        self.observer.stop()
        self.observer.join()


class EventFilter:
    """Класс для фильтрации событий из журнала."""

    def __init__(self, log_file):
        self.log_file = log_file

    def filter_events(self, event_type=None, user=None, start_time=None, end_time=None):
        with open(self.log_file, "r") as log:
            events = [json.loads(line) for line in log]

        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        if user:
            events = [e for e in events if e["user"] == user]
        if start_time:
            events = [e for e in events if datetime.strptime(e["timestamp"], "%Y-%m-%d %H:%M:%S") >= start_time]
        if end_time:
            events = [e for e in events if datetime.strptime(e["timestamp"], "%Y-%m-%d %H:%M:%S") <= end_time]

        return events


class ReportGenerator:
    """Класс для создания отчетов."""

    @staticmethod
    def generate_statistics(events, output_file="report.png"):
        event_types = [event["event_type"] for event in events]
        stats = {event: event_types.count(event) for event in set(event_types)}

        plt.bar(stats.keys(), stats.values())
        plt.title("Event Statistics")
        plt.xlabel("Event Type")
        plt.ylabel("Count")
        plt.savefig(output_file)
        print(f"Report saved to {output_file}.")


class AlertSystem:
    """Класс для отправки оповещений."""

    @staticmethod
    def send_email_alert(to_email, subject, body):
        from_email = "your_email@gmail.com"
        password = "your_password"

        message = MIMEMultipart()
        message["From"] = from_email
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, message.as_string())
            server.quit()
            print(f"Email alert sent to {to_email}.")
        except Exception as e:
            print(f"Failed to send email alert: {e}")


def rotate_logs(log_file, max_size=1024 * 1024, backup_count=5):
    """Функция ротации логов."""
    if os.path.exists(log_file) and os.path.getsize(log_file) >= max_size:
        for i in range(backup_count - 1, 0, -1):
            backup_file = f"{log_file}.{i}"
            next_backup = f"{log_file}.{i + 1}"
            if os.path.exists(backup_file):
                os.rename(backup_file, next_backup)
        os.rename(log_file, f"{log_file}.1")
        print("Log rotation completed.")


def main():
    log_file = "system_events.log"
    monitor_path = "/path/to/monitor"

    # Старт мониторинга
    monitor = EventMonitor(monitor_path, log_file)
    monitor_thread = threading.Thread(target=monitor.start)
    monitor_thread.start()

    try:
        while True:
            time.sleep(10)
            rotate_logs(log_file)

            # Отправка оповещения при определенных событиях
            filter_system = EventFilter(log_file)
            events = filter_system.filter_events(event_type="DELETED")
            if events:
                AlertSystem.send_email_alert(
                    to_email="recipient_email@gmail.com",
                    subject="Alert: Files Deleted",
                    body=f"{len(events)} files were deleted. Check the logs for details."
                )

    except KeyboardInterrupt:
        monitor.stop()
        print("Monitoring stopped.")


if __name__ == "__main__":
    main()
