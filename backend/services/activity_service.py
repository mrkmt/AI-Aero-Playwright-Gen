import time
from typing import List, Dict, Any
from datetime import datetime

class ActivityService:
    def __init__(self, max_logs: int = 50):
        self.logs: List[Dict[str, Any]] = []
        self.max_logs = max_logs

    def add_log(self, message: str, level: str = "info", agent: str = "System"):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "time_display": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "level": level,
            "agent": agent
        }
        self.logs.insert(0, log_entry) # Newest first
        if len(self.logs) > self.max_logs:
            self.logs.pop()
        
        # Also print to terminal for debugging
        print(f"📡 [Activity] {agent}: {message}")

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs

# Singleton instance
activity_service = ActivityService()
