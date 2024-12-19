from src.event_monitor import EventMonitor
from src.logger import Logger
from src.event_filter import EventFilter
from src.notification import Notification
from src.report_generator import ReportGenerator

def main():
    # Инициализация модулей
    logger = Logger("logs/event_log.txt")
    monitor = EventMonitor(logger)
    filter = EventFilter("logs/event_log.txt")
    notifier = Notification()
    report_gen = ReportGenerator("logs/event_log.txt")
    
    # Запуск мониторинга
    try:
        print("Starting system audit tool...")
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nStopping system audit tool.")
        monitor.stop_monitoring()
    
    # Функции фильтрации
    events = filter.filter_by_user("root")
    print("Filtered events:", events)
    
    # Оповещение
    notifier.send_email("hanglider76@icloud.com", "Audit Alert", "Suspicious activity detected.")
    
    # Генерация отчета
    report_gen.generate_summary_report()

if __name__ == "__main__":
    main()
