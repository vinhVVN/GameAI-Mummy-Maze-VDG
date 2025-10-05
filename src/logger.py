
import os

class Logger:
    def __init__(self, filename="log.txt"):
        project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.filepath = os.path.join(project_path, filename)
        self.live_logs = []

    def log(self, message):
        self.live_logs.append(message)

    def clear(self):
        self.live_logs = []
        with open(self.filepath, "w", encoding='utf-8') as f:
            f.write(f"--- New Session Started ---\n")

    def get_live_logs(self):
        return self.live_logs

    def save_to_file(self):
        """Ghi toàn bộ log trong bộ nhớ ra file."""
        with open(self.filepath, "a", encoding='utf-8') as f:
            for line in self.live_logs:
                f.write(line + "\n")