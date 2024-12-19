import matplotlib.pyplot as plt

class ReportGenerator:
    def __init__(self, log_file):
        self.log_file = log_file

    def generate_summary_report(self):
        with open(self.log_file, "r") as file:
            lines = file.readlines()

        events = {}
        for line in lines:
            event_type = line.split(" | ")[1]
            events[event_type] = events.get(event_type, 0) + 1

        plt.bar(events.keys(), events.values())
        plt.title("Event Summary")
        plt.xlabel("Event Type")
        plt.ylabel("Count")
        plt.savefig("logs/summary_report.png")
