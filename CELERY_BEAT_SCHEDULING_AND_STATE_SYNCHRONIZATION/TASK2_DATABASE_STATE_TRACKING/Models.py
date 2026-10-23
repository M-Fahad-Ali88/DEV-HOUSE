
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class TaskState:
    task_id: str
    task_name: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


def current_timestamp():
    return datetime.now(timezone.utc).isoformat()
