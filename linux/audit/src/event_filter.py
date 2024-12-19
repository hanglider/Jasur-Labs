class EventFilter:
    def __init__(self, log_file):
        self.log_file = log_file

    def filter_by_user(self, username):
        with open(self.log_file, "r") as file:
            lines = file.readlines()
        return [line for line in lines if f"User: {username}" in line]

    def filter_by_event_type(self, event_type):
        with open(self.log_file, "r") as file:
            lines = file.readlines()
        return [line for line in lines if f"{event_type}" in line]
