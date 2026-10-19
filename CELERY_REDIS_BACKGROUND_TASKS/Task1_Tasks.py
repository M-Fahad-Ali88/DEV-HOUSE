from celery import Celery
from pathlib import Path

app = Celery(
    "background_tasks",
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

@app.task
def process_file(file_path: str):
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    return {
        "status": "SUCCESS",
        "file_name": path.name,
        "characters": len(content),
    }
