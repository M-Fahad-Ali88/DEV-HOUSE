from celery import Celery
from pathlib import Path

app = Celery(
    "retry_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    result_expires=3600,
)


@app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(PermissionError, OSError),
    retry_backoff=True,
    retry_backoff_max=30,
    retry_jitter=False,
)
def process_file(self, file_path: str, simulate_failures: int = 0):
    path = Path(file_path)

    if self.request.retries < simulate_failures:
        raise PermissionError("Simulated temporary file-access failure")

    content = path.read_text(encoding="utf-8")

    return {
        "status": "SUCCESS",
        "file_name": path.name,
        "characters": len(content),
        "retries": self.request.retries,
    }
