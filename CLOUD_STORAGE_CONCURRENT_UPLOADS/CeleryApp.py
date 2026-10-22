
import os
from pathlib import Path

from celery import Celery
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Celery(
    "cloud_storage_uploads",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend="redis://localhost:6379/1",
    include=["TASKS.UploadTasks"],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    imports=("TASKS.UploadTasks",),
)
